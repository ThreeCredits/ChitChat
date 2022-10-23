from ctypes import alignment
import os
import tkinter as tk
from chat import *
from constants import *
from PIL import ImageTk, Image

from typing import Tuple, Any, List





root = None
hidden_root = None


images = None


class GUI:
    pass

class ScrollableFrame(tk.Frame):
    def __init__(self, parentObject, background, separator_color = None):
        tk.Frame.__init__(self, parentObject, background = background)
        self.canvas = tk.Canvas(self, borderwidth=0, background = background, highlightthickness=0)
        self.frame = tk.Frame(self.canvas, background = background)

        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, background=background)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.grid(row=0, column=1, sticky = "ns")

        if separator_color:
            tk.Frame(self, bg = separator_color).grid(row = 0, column = 2)

        self.canvas.grid(row=0, column=0, sticky = "news")
        self.window = self.canvas.create_window(0,0, window=self.frame, anchor = "nw", tags="self.frame")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame.bind("<Configure>", self.reset_scroll_region)
        self.canvas.bind("<Configure>", self.on_canvas_configure)


    def reset_scroll_region(self, event = None):
        #Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        #print("setting scroll region to",self.canvas.bbox("all"))
        

    def on_canvas_configure(self, event):
        #Resize the inner frame to match the canvas
        minWidth = self.frame.winfo_reqwidth()
        minHeight = self.frame.winfo_reqheight()

        if self.winfo_width() >= minWidth:
            newWidth = self.winfo_width()
        else:
            newWidth = minWidth


        if self.winfo_height() >= minHeight:
            newHeight = self.winfo_height()
            #Hide the scrollbar when not needed
            self.vsb.grid_remove()
        else:
            newHeight = minHeight
            #Show the scrollbar when needed
            self.vsb.grid()

        self.canvas.configure(width = 200) # weird fix
        self.canvas.itemconfig(self.window, width=newWidth, height=newHeight)



class ChatPreview(tk.Frame):
    """
    Creates a frame that allows to visualize the preview (name, picture, last message) of a given chat.
    """
    def __init__(self, parentObject, gui: GUI, chat: Chat):
        global images
        tk.Frame.__init__(self, parentObject, background = APP_MAIN_COLOR_DARK)
        self.chat = chat
        self.gui = gui
        
        self.grid_columnconfigure(0, weight = 0)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        b = tk.Button(self, image = images[chat.image_name], bd = 0,border = 0, background = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK, width = 50, height = 50, command = self.on_click)
        b.grid(row = 0, column = 0)

        chat_info_frame = tk.Frame(self, bg = APP_MAIN_COLOR)
        chat_info_frame.grid_rowconfigure(0, weight = 1)
        chat_info_frame.grid_rowconfigure(1, weight = 1)
        chat_info_frame.grid_columnconfigure(0, weight = 1)
        chat_info_frame.grid(row = 0, column = 1, sticky = "news")

        chat_name_frame = tk.Frame(chat_info_frame, bg = APP_MAIN_COLOR)
        tk.Label(chat_name_frame, text = chat.chat_name, fg = APP_BG_COLOR, bg = APP_MAIN_COLOR, font = ("Segoe UI", 12, "bold")).pack(side = tk.LEFT)
        chat_name_frame.grid(row = 0, column = 0, sticky = "ew")

        chat_preview_frame = tk.Frame(chat_info_frame, bg = APP_MAIN_COLOR)
        tk.Label(chat_preview_frame, text = chat.messages[-1].content, fg = APP_BG_COLOR, bg = APP_MAIN_COLOR).pack(side = tk.LEFT)
        chat_preview_frame.grid(row = 1, column = 0, sticky = "news")

        #self.bind("<Button-1>", self.on_click)

    
    def on_click(self) -> None:
        print("triggered")
        self.gui.current_chat = self.chat
        self.gui.load_messages()


class MessageFrame(tk.Frame):
    def __init__(self, gui: GUI, message: ChatMessage):
        tk.Frame.__init__(self, gui.messages_canvas.frame, bg = APP_BG_COLOR)

        if type(message.content) == str:
            msg_frame = tk.Label(self , text = message.content, font = ("Segoe UI", 10), wraplengt = 200, fg = APP_BG_COLOR, bg = APP_MAIN_COLOR, justify = tk.LEFT)
        else: msg_frame = None #TODO

        if message.chat.users[message.author] == gui.user_name:
            msg_frame.grid(row = 0, column = 0)

            tail_frame = tk.Frame(self, bg = APP_BG_COLOR)
            tk.Label(tail_frame, image = images["messageTailR"], border = 0).grid(row = 0, column = 0)
            tk.Frame(tail_frame, bg = APP_BG_COLOR).grid(row = 1, column = 0, sticky = "ns")
            tail_frame.grid(row = 0, column = 1, sticky = "ns")

            self.pack(anchor = "e", padx = 27, pady = 3)
        else:
            msg_frame.grid(row = 0, column = 1)

            tail_frame = tk.Frame(self, bg = APP_BG_COLOR)
            tk.Label(tail_frame, image = images["messageTailL"], border = 0).grid(row = 0, column = 0)
            tk.Frame(tail_frame, bg = APP_BG_COLOR).grid(row = 1, column = 0, sticky = "ns")
            tail_frame.grid(row = 0, column = 0, sticky = "ns")

            self.pack(anchor = "w", padx = 10, pady = 3)

class GUI:
    def __init__(self, title: str, size: Tuple[int, int]):
        global root, hidden_root, images
        self.title = title
        
        # Creating a hidden window that handles the minimization of the main window
        hidden_root = tk.Tk()
        hidden_root.geometry("0x0")
        hidden_root.configure(background = APP_MAIN_COLOR)
        hidden_root.attributes('-alpha', 0)
        hidden_root.iconbitmap("icon.ico")
        hidden_root.title(title)

        # Creating the main window
        root = tk.Toplevel(hidden_root)
        root.transient(hidden_root)
        root.geometry(str(size[0]) + "x" + str(size[1]))
        root.minsize(width = MIN_SIZE[0], height = MIN_SIZE[1]) 
        # removing frame
        root.overrideredirect(True)

        root.bind('<Button>', GUI.on_focus)
        hidden_root.bind('<FocusIn>', GUI.on_focus)

        # Account
        self.user_name = "Bruno Montalto"
        self.status = STATUS_ONLINE

        c = Chat("user", "user", users = ["Bruno Montalto", "user"])
        c2 = Chat("Fabbio", "Bruno Montalto", users = ["Bruno Montalto", "user"])
        for i in range(20):
            c.append_messages(ChatMessage(c, 1, datetime.datetime.now(), "This is a message"), ChatMessage(c, 0, datetime.datetime.now(), "This is a longer message to test if the wrapping is working correctly"))
        for i in range(10):
            c2.append_messages(ChatMessage(c, 1, datetime.datetime.now(), "This is a different message"), ChatMessage(c, 0, datetime.datetime.now(), "This is an answer to the different message"))
        self.chats = [c, c2]
        self.current_chat = self.chats[0]

        GUI.load_images()
        self.init_widgets()
        self.load_chats()
        self.load_messages()


        root.bind("<Configure>", GUI.on_resize)
        root.start_x = None
        root.start_y = None
        root.old_pos = GUI.center(*size)
        root.old_size = size
        

        root.mainloop()




    @staticmethod
    def on_resize(event: Any) -> None:
        """
        Fixes the proportion between the side panel and the main frame when the window is resized
        """
        global root
        if event.widget.widgetName == "toplevel":
            #print("resize to w:", event.width, "h:", event.height)
            #1/7 = 0.14285714285714285,   0.2857142857142857
            """perc = (event.width - MIN_SIZE[0])/(root.winfo_screenwidth() - MIN_SIZE[0])
            p2 = (1 + perc)/7
            p2 *= root.winfo_screenwidth()
            p2 = round(p2)
            root.winfo_children()[0].grid_columnconfigure(0, weight= MIN_SIZE[0])
            root.winfo_children()[0].grid_columnconfigure(1, weight= root.winfo_screenwidth() * p2)"""
            perc = (event.width - MIN_SIZE[0])/(root.winfo_screenwidth() - MIN_SIZE[0])
            p2 = (0.7 + perc)/7
            p2 *= root.winfo_screenwidth()
            p2 = round(p2)
            root.winfo_children()[0].grid_columnconfigure(0, weight = 100)
            root.winfo_children()[0].grid_columnconfigure(1, weight = p2)

          
    @staticmethod
    def center(width: int, height: int) -> Tuple[int, int]:
        """
        Centers the window in the screen.
        Returns the window position.
        """
        global root
        x = root.winfo_screenwidth()/2 - width/2
        y = root.winfo_screenheight()/2 - height/2
        root.geometry('+%d+%d'%(x,y))
        return x, y

    @staticmethod
    def get_mouse_position() -> Tuple[int, int]:
        return root.winfo_pointerx() + root.winfo_x(), root.winfo_pointery() + root.winfo_y()

    @staticmethod
    def start_move(event: Any) -> None:
        global root
        #print("start", event.x, event.y)
        if GUI.is_fullscreen():
            #root.geometry('%dx%d' % root.old_size)
            GUI.toggle_fullscreen(False)
            mx, my = GUI.get_mouse_position()
            #root.geometry('+%d+%d'% (mx - 100 , my))
            root.start_x = event.x//root.old_size[0]
            root.start_y = event.y//root.old_size[1]
        else:
            root.start_x = event.x
            root.start_y = event.y
        

    @staticmethod
    def stop_move(event: Any) -> None:
        global root
        root.start_x = None
        root.start_y = None
        if GUI.get_mouse_position()[1] < 5:
            GUI.toggle_fullscreen()

    @staticmethod
    def do_move(event: Any) -> None:
        global root
        deltax = event.x - root.start_x
        deltay = event.y - root.start_y
        x = root.winfo_x() + deltax
        y = root.winfo_y() + deltay
        root.geometry(f"+{x}+{y}")

    @staticmethod
    def minimize() -> None:
        global hidden_root
        hidden_root.iconify()

    @staticmethod
    def quit() -> None:
        global hidden_root
        hidden_root.destroy()

    @staticmethod
    def on_focus(event: Any) -> None:
        global root
        root.lift()
    
    @staticmethod
    def is_fullscreen() -> bool:
        global root
        return root.winfo_width() == root.winfo_screenwidth() and root.winfo_height() == root.winfo_screenheight()

    @staticmethod
    def toggle_fullscreen(position_reset = True) -> None:
        """
        If the app is in fullscreen, resets it to its previous size and position, otherwise resizes it in fullscreen
        """
        global root
        if GUI.is_fullscreen():
            if position_reset:
                root.geometry('%dx%d+%d+%d' % (*root.old_size, *root.old_pos))
            else:
                root.geometry('%dx%d' % root.old_size)
            root.winfo_children()[0].winfo_children()[1].winfo_children()[0].winfo_children()[2].config(image = images["dimension21"])
            return 

        root.old_pos = (root.winfo_x(), root.winfo_y())
        root.old_size = (root.winfo_width(), root.winfo_height())
        root.geometry('%dx%d+%d+%d' % (root.winfo_screenwidth(), root.winfo_screenheight(), 0, 0))
        root.winfo_children()[0].winfo_children()[1].winfo_children()[0].winfo_children()[2].config(image = images["dimension1"])

    @staticmethod
    def load_images() -> None:
        """
        Loads the buttons images.
        """
        global images
        images = {
            "messageTailL" : ImageTk.PhotoImage(Image.open("sprites/messageTailL.png")),
            "messageTailR" : ImageTk.PhotoImage(Image.open("sprites/messageTailR.png"))
        }

        for filename in os.listdir("sprites/profile pics"):
            if filename.endswith(".png"):
                images[filename.replace(".png", "")] = tk.PhotoImage(file = "sprites/profile pics/" + filename)
        for filename in os.listdir("sprites/buttons"):
            if filename.endswith(".png"):
                images[filename.replace(".png", "")] = tk.PhotoImage(file = "sprites/buttons/" + filename)
    

    def load_chats(self):
        for chat in self.chats:
            tk.Frame(self.chats_canvas.frame, bg = APP_MAIN_COLOR_DARK).pack(fill = tk.X)

            chat_preview = ChatPreview(self.chats_canvas.frame, self, chat)

            chat_preview.pack(fill = tk.X)



    def load_messages(self):
        # Destroy & create new scrollable frame
        self.messages_canvas.grid_forget()
        self.messages_canvas.destroy()
        del self.messages_canvas
        self.messages_canvas = ScrollableFrame(self.main_frame, background = APP_BG_COLOR)
        self.messages_canvas.grid(row = 2, column = 0, sticky = "news")
        
        for message in self.current_chat.messages:
            MessageFrame(self, message)
        
        # Fix scroll region and scroll to the bottom
        for i in range(2):
            self.messages_canvas.frame.update_idletasks()
            self.messages_canvas.on_canvas_configure(None)
            self.messages_canvas.canvas.yview("moveto", "1.0")
    
    



    def init_widgets(self) -> None:
        """
        Creates the window structure and main components
        """
        #TODO: Ci sono molti self. inutili

        global root, images
        # Create main container
        self.main_container = tk.Frame(root)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=3)
        self.main_container.grid_rowconfigure(0, weight = 1)
        self.main_container.pack(expand=True, fill = tk.BOTH)

        #* --- SIDE PANEL FRAME --- #
        side_panel_frame = tk.Frame(self.main_container, bg = APP_MAIN_COLOR)
        side_panel_frame.grid_rowconfigure(0, weight = 0)
        side_panel_frame.grid_rowconfigure(1, weight = 1)
        side_panel_frame.grid_columnconfigure(0, weight = 1)
        side_panel_frame.grid(row = 0, column = 0, sticky = "news")


        #** Profile & searchbar frame
        profile_sbar_frame = tk.Frame(side_panel_frame)
        profile_sbar_frame.grid_rowconfigure(0, weight=0)
        profile_sbar_frame.grid_rowconfigure(1, weight=1)
        profile_sbar_frame.grid_columnconfigure(0, weight = 1)
        profile_sbar_frame.grid(row = 0, column = 0, sticky = "news")


        #*** Profile frame
        profile_frame = tk.Frame(profile_sbar_frame, background = APP_MAIN_COLOR)
        profile_frame.grid_columnconfigure(0, weight= 0)
        profile_frame.grid_columnconfigure(1, weight=1)
        profile_frame.grid_rowconfigure(0, weight = 1)
        profile_frame.grid(row = 0, column = 0, sticky = "news")
        

        #**** Profile pic 
        c = tk.Button(profile_frame, image = images["Bruno Montalto"], border = 0, background = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK, width = 60, height = 60)
        c.grid(row = 0, column = 0, sticky = "news")

        #**** Profile info frame
        profile_info_frame = tk.Frame(profile_frame, background = APP_MAIN_COLOR)
        profile_info_frame.grid_rowconfigure(0, weight = 0)
        profile_info_frame.grid_rowconfigure(1, weight = 1)
        profile_info_frame.grid_columnconfigure(0, weight = 1)
        profile_info_frame.grid(row = 0, column = 1, sticky = "news")

        #***** Username and buttons
        username_buttons_frame = tk.Frame(profile_info_frame, background = APP_MAIN_COLOR)
        username_buttons_frame.bind('<ButtonPress-1>', GUI.start_move)
        username_buttons_frame.bind('<ButtonRelease-1>', GUI.stop_move)
        username_buttons_frame.bind('<B1-Motion>', GUI.do_move)
        username_buttons_frame.grid(row = 0, column = 0, sticky = "news")

        username = tk.Label(username_buttons_frame, text = self.user_name, font = ("Segoe UI", 12, "bold"), background = APP_MAIN_COLOR, fg = APP_BG_COLOR)
        username.pack(side = tk.LEFT)
        username.bind('<ButtonPress-1>', GUI.start_move)
        username.bind('<ButtonRelease-1>', GUI.stop_move)
        username.bind('<B1-Motion>', GUI.do_move)

        more_button = tk.Button(username_buttons_frame, image = images["more"], border = 0, background = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK)
        more_button.pack(side = tk.RIGHT, fill = tk.Y)

        settings_button = tk.Button(username_buttons_frame, image = images["settings"], border = 0, background = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK)
        settings_button.pack(side = tk.RIGHT, fill = tk.Y)

        #***** Status
        status_frame = tk.Frame(profile_info_frame, background = APP_MAIN_COLOR)
        status_frame.grid(row = 1, column=0, sticky = "news")
        tk.Label(status_frame, text = STATUS_STRING[self.status], background = APP_MAIN_COLOR, fg = APP_BG_COLOR).pack(side = tk.LEFT)


        #*** Search bar frame
        sbar_frame = tk.Frame(profile_sbar_frame, background = APP_MAIN_COLOR_DARK)
        sbar_frame.grid(row = 1, column = 0, sticky = "news")

        tk.Label(sbar_frame, text = "Search messages", background = APP_MAIN_COLOR_DARK, fg = APP_BG_COLOR).pack()
        tk.Entry(sbar_frame, border = 0).pack(fill = tk.X, padx = 5, pady = 5)


        # Chats container
        self.chats_canvas = ScrollableFrame(side_panel_frame, background = APP_MAIN_COLOR_DARK, separator_color = APP_MAIN_COLOR)
        self.chats_canvas.grid(row = 1, column = 0, sticky = "news")

        #tk.Label(self.side_panel_frame, text = "side panel").pack()

        #* --- MAIN FRAME --- #
        main_frame = tk.Frame(self.main_container, bg = APP_BG_COLOR)
        self.main_frame = main_frame #TODO
        main_frame.grid_rowconfigure(0, weight = 0)
        main_frame.grid_rowconfigure(1, weight = 0)
        main_frame.grid_rowconfigure(2, weight = 1)
        main_frame.grid_rowconfigure(3, weight = 0)
        main_frame.grid_rowconfigure(4, weight = 0)
        main_frame.grid_columnconfigure(0, weight = 1)
        main_frame.grid(row = 0, column = 1, sticky = "news")

        #** Title bar 
        self.titleBar = tk.Frame(main_frame, bg = APP_BG_COLOR)
        #*** Close button
        tk.Button(self.titleBar, image = images["close1"], border = 0, command = GUI.quit).pack(side = tk.RIGHT)
        tk.Frame(self.titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        #*** Resize button
        self.resize_button = tk.Button(self.titleBar, image = images["dimension21"], border = 0, command = GUI.toggle_fullscreen).pack(side = tk.RIGHT)
        tk.Frame(self.titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        #*** Minimize button
        tk.Button(self.titleBar, image = images["minimize1"], border = 0, command = GUI.minimize).pack(side = tk.RIGHT)
        tk.Frame(self.titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        t = tk.Label(self.titleBar, text = self.title, bg = APP_BG_COLOR)
        t.pack(side = tk.LEFT)

        self.titleBar.grid(row = 0, column = 0, sticky = "news")
        t.bind('<ButtonPress-1>', GUI.start_move)
        t.bind('<ButtonRelease-1>', GUI.stop_move)
        t.bind('<B1-Motion>', GUI.do_move)
        self.titleBar.bind('<ButtonPress-1>', GUI.start_move)
        self.titleBar.bind('<ButtonRelease-1>', GUI.stop_move)
        self.titleBar.bind('<B1-Motion>', GUI.do_move)

        #** Horizonatal separator
        tk.Frame(main_frame, bg = APP_MAIN_COLOR).grid(row = 1, column = 0, sticky = "ew")

        #** Messages frame
        self.messages_canvas = ScrollableFrame(main_frame, background = APP_BG_COLOR)
        self.messages_canvas.grid(row = 2, column = 0, sticky = "news")

        #** Horizonatal separator
        tk.Frame(main_frame, bg = APP_MAIN_COLOR).grid(row = 3, column = 0, sticky = "ew")

        #** Entry & send button
        entry_send = tk.Frame(main_frame, background = APP_BG_COLOR)
        entry_send.grid_columnconfigure(0, weight = 1)
        entry_send.grid_columnconfigure(1, weight = 0)
        entry_send.grid_columnconfigure(2, weight = 0)
        entry_send.grid_rowconfigure(0, weight = 1)
        entry_send.grid(row = 4, column = 0, sticky = "news")

        self.entry = tk.Entry(entry_send, background = APP_BG_COLOR_DARK, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = ("Segoe UI", 12))
        self.entry.grid(row = 0, column = 0, sticky = "news", padx = 15, pady = 5)
        tk.Button(entry_send, image = images["send"], border = 0, background = APP_BG_COLOR, command = self.foo).grid(row = 0, column = 1, sticky = "news")
        tk.Label(entry_send, text = "  ", background = APP_BG_COLOR).grid(row = 0, column = 2)
    

    def foo(self):
        print("foo")
                
        MessageFrame(self, ChatMessage(self.current_chat, 0, datetime.datetime.now(), self.entry.get()))
        # Fix scroll region and scroll to the bottom
        for i in range(2): 
            self.messages_canvas.frame.update_idletasks()
            self.messages_canvas.on_canvas_configure(None)
            self.messages_canvas.canvas.yview("moveto", "0")




