import os
import tkinter as tk

from chat import *
from constants import *
from PIL import ImageTk, Image
from typing import Tuple, Any, List



images = None


class GUI:
    pass


class ScrollableFrame(tk.Frame):
    """
    Creates a frame with a scrollable canvas and a vertical scollbar inside.
    """
    def __init__(self, parentObject: tk.Frame, bg: Tuple[int, int, int], separator_color = None) -> None:
        """
        :param parentObject: will contain this scrollable frame
        :param bg: the background color
        :param separator_color: if not None, creates a vertical separator on the left of the scrollbar
        """
        self.separator_color = separator_color
        tk.Frame.__init__(self, parentObject, bg = bg)
        self.canvas = tk.Canvas(self, borderwidth=0, bg = bg, highlightthickness=0)
        self.canvas.configure(width = 0) # weird fix
        self.frame = tk.Frame(self.canvas, bg = bg)

        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, bg = bg)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.grid(row=0, column=1, sticky = "ns")

        if separator_color:
            tk.Frame(self, bg = separator_color).grid(row = 0, column = 2)

        self.canvas.grid(row = 0, column = 0, sticky = "news")
        self.window = self.canvas.create_window(0, 0, window = self.frame, anchor = "nw", tags = "self.frame")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.frame.bind("<Configure>", self.reset_scroll_region)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)


    def on_mousewheel(self, event: tk.Event) -> None:
        """
        Allows to scroll the canvas window with the mouse wheel.
        """
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


    def reset_scroll_region(self, event: tk.Event = None) -> None:
        """
        Resets the scroll region to encompass the inner frame.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        

    def on_canvas_configure(self, event: tk.Event) -> None:
        """
        Resizes the inner frame to match the canvas.
        """
        minWidth = self.frame.winfo_reqwidth()
        minHeight = self.frame.winfo_reqheight()

        if self.winfo_width() >= minWidth:
            newWidth = self.winfo_width()
        else:
            newWidth = minWidth


        if self.winfo_height() >= minHeight:
            newHeight = self.winfo_height()
            #Hide the scrollbar when not needed
            if self.separator_color:
                self.vsb.grid_forget()
        else:
            newHeight = minHeight
            #Show the scrollbar when needed
            self.vsb.grid(row=0, column=1, sticky = "ns")

        self.canvas.itemconfig(self.window, width=newWidth, height=newHeight)



class ChatPreview(tk.Frame):
    """
    Creates a frame that allows to visualize the preview (name, picture, last message) of a given chat.
    """
    def __init__(self, parentObject: tk.Frame, gui: GUI, chat: Chat) -> None:
        """
        :param parentObject: will contain the chat preview
        :param gui: the gui object where this widget is contained (needed to access chats)
        :param chat: the chat to display
        """
        global images
        tk.Frame.__init__(self, parentObject, background = APP_MAIN_COLOR_DARK)
        self.chat = chat
        self.gui = gui
        
        self.grid_columnconfigure(0, weight = 0)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        img = tk.Label(self, image = images[chat.image_name], border = 0, bg = APP_MAIN_COLOR)
        img.grid(row = 0, column = 0)

        chat_info_frame = tk.Frame(self, bg = APP_MAIN_COLOR)
        chat_info_frame.grid_rowconfigure(0, weight = 1)
        chat_info_frame.grid_rowconfigure(1, weight = 1)
        chat_info_frame.grid_columnconfigure(0, weight = 1)
        chat_info_frame.grid(row = 0, column = 1, sticky = "news")

        chat_name_frame = tk.Frame(chat_info_frame, bg = APP_MAIN_COLOR)
        l1 = tk.Label(chat_name_frame, text = chat.chat_name, fg = APP_BG_COLOR, bg = APP_MAIN_COLOR, font = ("Segoe UI", 12, "bold"))
        l1.pack(side = tk.LEFT)
        chat_name_frame.grid(row = 0, column = 0, sticky = "ew")

        chat_preview_frame = tk.Frame(chat_info_frame, bg = APP_MAIN_COLOR)
        l2 = tk.Label(chat_preview_frame, text = chat.messages[-1].content, fg = APP_BG_COLOR, bg = APP_MAIN_COLOR)
        l2.pack(side = tk.LEFT)
        chat_preview_frame.grid(row = 1, column = 0, sticky = "news")

        self.widgets = [self, chat_info_frame, chat_name_frame, chat_preview_frame, l1, l2, img]
        
        for w in self.widgets:
            w.bind("<ButtonPress-1>", self.on_press)
            w.bind("<ButtonRelease-1>", self.on_release)
    

    def on_press(self, event: tk.Event) -> None:
        """
        Makes all the subwidgets background darker.
        """
        for w in self.widgets:
            w.configure(bg = APP_MAIN_COLOR_DARK)


    def on_release(self, event: tk.Event) -> None:
        """
        Makes all the subwidgets background lighter.
        """
        for w in self.widgets:
            w.configure(bg = APP_MAIN_COLOR)
        
        self.gui.current_chat = self.chat
        self.gui.load_messages()


class MessageFrame(tk.Frame):
    """
    Creates a speech ballon style message and packs it.
    """
    def __init__(self, gui: GUI, message: ChatMessage) -> None:
        """
        :param gui: the gui object (contains the messages frame)
        :param message: the message to display
        """
        tk.Frame.__init__(self, gui.messages_canvas.frame, bg = APP_BG_COLOR)

        if type(message.content) == str:
            msg_frame = tk.Label(self , text = message.content, font = ("Segoe UI", 10), wraplengt = 250, fg = APP_BG_COLOR, bg = APP_MAIN_COLOR, justify = tk.LEFT)
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


class GUI(tk.Toplevel):
    def __init__(self, title: str, size: Tuple[int, int]) -> None:
        global images
        
        self.title_ = title

        # Creating a hidden window that handles the minimization of the main window
        self.hidden_root = tk.Tk()
        self.hidden_root.geometry("0x0")
        self.hidden_root.configure(background = APP_MAIN_COLOR)
        self.hidden_root.attributes('-alpha', 0)
        self.hidden_root.iconbitmap("icon.ico")
        self.hidden_root.title(title)
        
        
        # Creating the main window
        tk.Toplevel.__init__(self, master = self.hidden_root)
        self.transient(self.hidden_root)
        self.geometry(str(size[0]) + "x" + str(size[1]))
        self.minsize(width = MIN_SIZE[0], height = MIN_SIZE[1]) 
        
        # removing frame
        self.overrideredirect(True)

        self.bind('<Button>', self.on_focus)
        self.hidden_root.bind('<FocusIn>', self.on_focus)

        # Account
        self.user_name = "Bruno Montalto"
        self.status = STATUS_ONLINE

        c = Chat("user", "user", users = ["Bruno Montalto", "user"])
        c2 = Chat("Fabbio", "Bruno Montalto", users = ["Bruno Montalto", "user"])
        for i in range(20):
            c.append_messages(ChatMessage(c, 1, datetime.datetime.now(), "This is a message"), ChatMessage(c, 0, datetime.datetime.now(), "This is a longer message to test if the wrapping is working correctly"))
        for i in range(4):
            c2.append_messages(ChatMessage(c, 1, datetime.datetime.now(), "This is a different message"), ChatMessage(c, 0, datetime.datetime.now(), "This is an answer to the different message"))
        self.chats = [c, c2]
        self.current_chat = self.chats[0]

        GUI.load_images()
        self.init_widgets()
        self.load_chats()
        self.load_messages()


        self.bind("<Configure>", self.on_resize)
        self.start_x = None
        self.start_y = None
        self.old_pos = self.center(*size)
        self.old_size = size
        

        self.mainloop()


    def on_resize(self, event: tk.Event) -> None:
        """
        Fixes the proportion between the side panel and the main frame when the window is resized
        """
        if event.widget.widgetName == "toplevel":
            perc = (event.width - MIN_SIZE[0])/(self.winfo_screenwidth() - MIN_SIZE[0])
            p2 = (0.7 + perc)/7
            p2 *= self.winfo_screenwidth()
            p2 = round(p2)
            self.winfo_children()[0].grid_columnconfigure(0, weight = 100)
            self.winfo_children()[0].grid_columnconfigure(1, weight = p2)


    def center(self, width: int, height: int) -> Tuple[int, int]:
        """
        Centers the window in the screen.
        Returns the window position.
        """
        x = self.winfo_screenwidth()/2 - width/2
        y = self.winfo_screenheight()/2 - height/2
        self.geometry('+%d+%d'%(x,y))
        return x, y


    def get_mouse_position(self) -> Tuple[int, int]:
        return self.winfo_pointerx() + self.winfo_x(), self.winfo_pointery() + self.winfo_y()

    
    def start_move(self, event: tk.Event) -> None:
        if self.is_fullscreen():
            self.toggle_fullscreen(False)
            mx, my = self.get_mouse_position()
            self.start_x = event.x//self.old_size[0]
            self.start_y = event.y//self.old_size[1]
        else:
            self.start_x = event.x
            self.start_y = event.y
        

    def stop_move(self, event: tk.Event) -> None:
        self.start_x = None
        self.start_y = None
        if self.get_mouse_position()[1] < 5:
            self.toggle_fullscreen()


    def do_move(self, event: tk.Event) -> None:
        deltax = event.x - self.start_x
        deltay = event.y - self.start_y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")


    def minimize(self) -> None:
        self.hidden_root.iconify()


    def quit(self) -> None:
        self.hidden_root.destroy()


    def on_focus(self, event: tk.Event) -> None:
        self.lift()
    
    
    def is_fullscreen(self) -> bool:
        return self.winfo_width() == self.winfo_screenwidth() and self.winfo_height() == self.winfo_screenheight()


    def toggle_fullscreen(self, position_reset: bool = True) -> None:
        """
        If the app is in fullscreen, resets it to its previous size and position, otherwise resizes it in fullscreen
        """
        if self.is_fullscreen():
            if position_reset:
                self.geometry('%dx%d+%d+%d' % (*self.old_size, *self.old_pos))
            else:
                self.geometry('%dx%d' % self.old_size)
            self.winfo_children()[0].winfo_children()[1].winfo_children()[0].winfo_children()[2].config(image = images["dimension21"])
            return 

        self.old_pos = (self.winfo_x(), self.winfo_y())
        self.old_size = (self.winfo_width(), self.winfo_height())
        self.geometry('%dx%d+%d+%d' % (self.winfo_screenwidth(), self.winfo_screenheight(), 0, 0))
        self.winfo_children()[0].winfo_children()[1].winfo_children()[0].winfo_children()[2].config(image = images["dimension1"])


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
                images[filename.replace(".png", "")] = ImageTk.PhotoImage(Image.open("sprites/profile pics/" + filename))
        for filename in os.listdir("sprites/buttons"):
            if filename.endswith(".png"):
                images[filename.replace(".png", "")] = ImageTk.PhotoImage(Image.open("sprites/buttons/" + filename))
    

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
        self.messages_canvas = ScrollableFrame(self.main_frame, bg = APP_BG_COLOR)
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

        global images
        # Create main container
        self.main_container = tk.Frame(self)
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
        username_buttons_frame.bind('<ButtonPress-1>', self.start_move)
        username_buttons_frame.bind('<ButtonRelease-1>', self.stop_move)
        username_buttons_frame.bind('<B1-Motion>', self.do_move)
        username_buttons_frame.grid(row = 0, column = 0, sticky = "news")

        username = tk.Label(username_buttons_frame, text = self.user_name, font = ("Segoe UI", 12, "bold"), background = APP_MAIN_COLOR, fg = APP_BG_COLOR)
        username.pack(side = tk.LEFT)
        username.bind('<ButtonPress-1>', self.start_move)
        username.bind('<ButtonRelease-1>', self.stop_move)
        username.bind('<B1-Motion>', self.do_move)

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
        self.chats_canvas = ScrollableFrame(side_panel_frame, bg = APP_MAIN_COLOR_DARK, separator_color = APP_MAIN_COLOR)
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
        tk.Button(self.titleBar, image = images["close1"], border = 0, command = self.quit).pack(side = tk.RIGHT)
        tk.Frame(self.titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        #*** Resize button
        self.resize_button = tk.Button(self.titleBar, image = images["dimension21"], border = 0, command = self.toggle_fullscreen).pack(side = tk.RIGHT)
        tk.Frame(self.titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        #*** Minimize button
        tk.Button(self.titleBar, image = images["minimize1"], border = 0, command = self.minimize).pack(side = tk.RIGHT)
        tk.Frame(self.titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        t = tk.Label(self.titleBar, text = self.title_, bg = APP_BG_COLOR)
        t.pack(side = tk.LEFT)

        self.titleBar.grid(row = 0, column = 0, sticky = "news")
        t.bind('<ButtonPress-1>', self.start_move)
        t.bind('<ButtonRelease-1>', self.stop_move)
        t.bind('<B1-Motion>', self.do_move)
        self.titleBar.bind('<ButtonPress-1>', self.start_move)
        self.titleBar.bind('<ButtonRelease-1>', self.stop_move)
        self.titleBar.bind('<B1-Motion>', self.do_move)

        #** Horizonatal separator
        tk.Frame(main_frame, bg = APP_MAIN_COLOR).grid(row = 1, column = 0, sticky = "ew")

        #** Messages frame
        self.messages_canvas = ScrollableFrame(main_frame, bg = APP_BG_COLOR)
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
            self.messages_canvas.canvas.yview("moveto", "1.0")




