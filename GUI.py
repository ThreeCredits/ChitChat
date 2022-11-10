import os
import tkinter as tk
from tkinter.ttk import Sizegrip

from chat import *
from cipher import *
from constants import *
from PIL import ImageTk, Image
import mouse
from typing import Tuple, Any, List


import socket, pickle
from identity import Identity
from message import *
from utils import *

from threading import Thread

s: socket.socket = None
self_identity: Identity = Identity()
server_identity: Identity = None
out_packet: Packet = Packet([])



class NoFrame(tk.Toplevel):
    """
    Creates a frameless tkinter window that is controlled by an hidden window.
    """
    def __init__(self, title: str, size: Tuple[int, int], bg: str = "white") -> None:
        """
        :param title: the title of the window
        :param size: a tuple containing the desired width and height
        :param bg: the background color
        """
        # Creating a hidden window that handles the minimization of the main window
        self.hidden_root: tk.Tk = tk.Tk()
        self.hidden_root.geometry("0x0")
        self.hidden_root.configure(background = APP_MAIN_COLOR)
        self.hidden_root.attributes('-alpha', 0)
        self.hidden_root.iconbitmap("icon.ico")
        self.hidden_root.title(title)
        
        
        # Creating the main window
        tk.Toplevel.__init__(self, master = self.hidden_root, bg = bg)
        #self.transient(self.hidden_root)
        self.geometry(str(size[0]) + "x" + str(size[1])) 
        
        # removing frame
        self.overrideredirect(True)

        self.bind('<Button>', self.on_focus)
        self.hidden_root.bind('<FocusIn>', self.on_focus)

        for i in range(2): self.old_pos: Tuple[int, int] = self.center()

        self.start_x: int = None
        self.start_y: int = None
        self.old_size: Tuple[int, int] = size

        self.on_focus(None)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.hidden_root.protocol("WM_DELETE_WINDOW", self.quit)


    def minimize(self) -> None:
        """
        minimized the window.
        """
        self.hidden_root.iconify()
        self.withdraw()

    def quit(self) -> None:
        """
        closes the window.
        """
        #print("closing")
        self.destroy()
        self.hidden_root.destroy()


    def on_focus(self, event: tk.Event) -> None:
        """
        lifts the window.
        """
        self.lift()
        self.deiconify()

 

    
    def center(self) -> Tuple[int, int]:
        """
        Centers the window in the screen.
        Returns the window position.
        """
        self.update()
        x = self.winfo_screenwidth()/2 - self.winfo_width()/2
        y = self.winfo_screenheight()/2 - self.winfo_height()/2
        self.geometry('+%d+%d'%(x,y))
        return x, y


    def start_move(self, event: tk.Event) -> None:
        """
        Called when the user starts dragging the window, toggles fullscreen if the window was fullscreen.
        """
        mx, my = mouse.get_position()
        if self.is_fullscreen():
            self.toggle_fullscreen(False)
            self.delta_x = self.old_size[0]//2
            self.delta_y = 15
            self.do_move(None)
        else:
            self.delta_x = mx - self.winfo_x()
            self.delta_y = my - self.winfo_y()

        

    def do_move(self, event: tk.Event) -> None:
        """
        Called during the window dragging, updates its position
        """
        mx, my = mouse.get_position()
        x = -self.delta_x + mx
        y = -self.delta_y + my
        self.geometry(f"+{x}+{y}")


    def stop_move(self, event: tk.Event) -> None:
        """
        Called when the user stops dragging the window, if the window is released on the top of the screen, it switches to fullscreen.
        """
        self.delta_x = None
        self.delta_y = None
        if mouse.get_position()[1] < 5:
            self.toggle_fullscreen()

    
    def is_fullscreen(self) -> bool:
        ":return: True if the window is on fullscreen, else False"
        return self.winfo_width() == self.winfo_screenwidth() and self.winfo_height() == self.winfo_screenheight()
    

    def toggle_fullscreen(self) -> None:
        """
        If the window is not fullscreen, it swhitches to fullscreen and viceversa.
        """
        return



class ScrollableFrame(tk.Frame):
    """
    Creates a frame with a scrollable canvas and a vertical scollbar inside.
    """
    def __init__(self, parent_object: tk.Frame, bg: Tuple[int, int, int], separator_color: str = None) -> None:
        """
        :param parent_object: will contain this scrollable frame
        :param bg: the background color
        :param separator_color: if not None, creates a vertical separator on the left of the scrollbar
        """
        self.separator_color: str = separator_color
        self.mouse_wheel_enabled: bool = False
        tk.Frame.__init__(self, parent_object, bg = bg)
        self.canvas: tk.Canvas = tk.Canvas(self, borderwidth=0, bg = bg, highlightthickness=0)
        self.canvas.configure(width = 0) # weird fix
        self.frame: tk.Frame = tk.Frame(self.canvas, bg = bg)

        self.vsb: tk.Scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, bg = bg)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.grid(row=0, column=1, sticky = "ns")

        if separator_color:
            tk.Frame(self, bg = separator_color).grid(row = 0, column = 2)

        self.canvas.grid(row = 0, column = 0, sticky = "news")
        self.window: tk._CanvasItemId = self.canvas.create_window(0, 0, window = self.frame, anchor = "nw", tags = "self.frame")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.frame.bind("<Configure>", self.reset_scroll_region)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        

        self.canvas.bind("<Enter>", self.on_mouse_over)
        self.canvas.bind("<Leave>", self.on_mouse_leave)


    def on_mouse_over(self, event: tk.Event):
        self.mouse_wheel_enabled = True
    

    def on_mouse_leave(self, event: tk.Event):
        self.mouse_wheel_enabled = False

    def on_mousewheel(self, event: tk.Event) -> None:
        """
        Allows to scroll the canvas window with the mouse wheel.
        """
        if self.mouse_wheel_enabled:
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
        for w in get_all_children(self.canvas):
            w.bind("<MouseWheel>", self.on_mousewheel)
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
    def __init__(self, parent_object: tk.Frame, gui: NoFrame, chat: Chat) -> None:
        """
        :param parent_object: will contain the chat preview
        :param gui: the gui object where this widget is contained (needed to access chats)
        :param chat: the chat to display
        """
        tk.Frame.__init__(self, parent_object, background = APP_MAIN_COLOR_DARK)
        self.chat: Chat = chat
        self.gui: NoFrame = gui
        
        self.grid_columnconfigure(0, weight = 0)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_rowconfigure(0, weight = 1)

        img = tk.Label(self, image = gui.images["user"], border = 0, bg = APP_MAIN_COLOR)
        img.grid(row = 0, column = 0)

        chat_info_frame = tk.Frame(self, bg = APP_MAIN_COLOR)
        chat_info_frame.grid_rowconfigure(0, weight = 1)
        chat_info_frame.grid_rowconfigure(1, weight = 1)
        chat_info_frame.grid_columnconfigure(0, weight = 1)
        chat_info_frame.grid(row = 0, column = 1, sticky = "news")

        chat_name_frame = tk.Frame(chat_info_frame, bg = APP_MAIN_COLOR)
        l1 = tk.Label(chat_name_frame, text = chat.chat_name, fg = APP_BG_COLOR, bg = APP_MAIN_COLOR, font = (APP_FONT, 12, "bold"))
        l1.pack(side = tk.LEFT)
        chat_name_frame.grid(row = 0, column = 0, sticky = "ew")

        chat_preview_frame = tk.Frame(chat_info_frame, bg = APP_MAIN_COLOR)
        l2 = tk.Label(chat_preview_frame, text = (chat.messages[-1].content[:min(len(chat.messages[-1].content), 15)] + ("..." if len(chat.messages[-1].content) > 15 else "") if len(chat.messages) > 0 else ""), fg = APP_BG_COLOR, bg = APP_MAIN_COLOR, font = (APP_FONT, 9))
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
        
        self.gui.entry.config(state = "normal")
        self.gui.current_chat = self.chat
        self.gui.app_title.config(text = "ChitChat - " + self.chat.chat_name)
        self.gui.load_message_frames()



class MessageFrame(tk.Frame):
    """
    Creates a speech ballon style message and packs it.
    """
    def __init__(self, gui: NoFrame, message: ChatMessage) -> None:
        """
        :param gui: the gui object (contains the messages frame)
        :param message: the message to display
        """
        tk.Frame.__init__(self, gui.messages_canvas.frame, bg = APP_BG_COLOR)

        if message.date.strftime("%m/%d/%Y") == datetime.datetime.now().strftime("%m/%d/%Y"):
            date = "today at " + message.date.strftime("%H:%M")
        else:
            date = message.date.strftime("%d/%m/%Y")
        if type(message.content) == str:
            msg_frame = tk.Frame(self, bg = APP_MAIN_COLOR)
            name_date_frame = tk.Frame(msg_frame, bg = APP_MAIN_COLOR)
            tk.Label(name_date_frame, text = message.author[0] + " #" + str(message.author[1]) + "   ", font = (APP_FONT, 11, "bold"), wraplengt = 290, fg = APP_BG_COLOR, bg = APP_MAIN_COLOR, justify = tk.LEFT).pack(side = tk.LEFT)
            tk.Label(name_date_frame, text =  date, font = (APP_FONT, 10), wraplengt = 280, fg = APP_BG_COLOR, bg = APP_MAIN_COLOR, justify = tk.LEFT).pack(side = tk.RIGHT)
            name_date_frame.pack(anchor = "w", fill = tk.X)

            tk.Frame(msg_frame, bg = APP_MAIN_COLOR_DARK).pack(fill = tk.X, padx = 1)
            
            self.text_label: tk.Label = tk.Label(msg_frame , text = message.content, font = (APP_FONT, 10), wraplengt = 280, fg = APP_BG_COLOR, bg = APP_MAIN_COLOR, justify = tk.LEFT)
            self.text_label.pack(anchor = "w")
        else: msg_frame = None #TODO

        if (message.author[0], message.author[1]) == (gui.user_name, gui.tag):
            msg_frame.grid(row = 0, column = 0)

            tail_frame = tk.Frame(self, bg = APP_BG_COLOR)
            tk.Label(tail_frame, image = gui.images["messageTailR"], border = 0).grid(row = 0, column = 0)
            tk.Frame(tail_frame, bg = APP_BG_COLOR).grid(row = 1, column = 0, sticky = "ns")
            tail_frame.grid(row = 0, column = 1, sticky = "ns")

            self.pack(anchor = "e", padx = 27, pady = 3)
        else:
            msg_frame.grid(row = 0, column = 1)

            tail_frame = tk.Frame(self, bg = APP_BG_COLOR)
            tk.Label(tail_frame, image = gui.images["messageTailL"], border = 0).grid(row = 0, column = 0)
            tk.Frame(tail_frame, bg = APP_BG_COLOR).grid(row = 1, column = 0, sticky = "ns")
            tail_frame.grid(row = 0, column = 0, sticky = "ns")

            self.pack(anchor = "w", padx = 10, pady = 3)



class ConnectGUI(NoFrame):
    def __init__(self) -> None:
        NoFrame.__init__(self, "ChitChat - Connect", CONNECT_SIZE, bg = APP_BG_COLOR)
        self.image: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open("sprites/icon.png"))

        self.create_title_bar()
        self.init_widgets()
        
        self.mainloop()

    
    def connect(self) -> None:
        """
        Tryes to start a connection with the given server.
        """
        global s, self_identity, server_identity

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            address = (self.server.get(), int(self.port.get()))
        except:
            self.error.config(text = "[Error] Invalid port")
            return

        try:
            s.connect(address)
        except Exception as e:
            self.error.config(text = str(e))
            return

        print("connected")
        try:
            msg = pickle.loads(s.recv(32 * 1024))
        except Exception as e:
            self.error.config(text = str(e))
            s.close()
            return

        if msg[0].type == "backoff": #TODO costanti
            self.error.config(text = "[Error] Blacklisted until " + str(msg[0].data))
            s.close()
            return
        server_identity = Identity(pub_bytes = msg[0].data)
        
        # send key
        s.send(pickle.dumps(
            Packet(
                [
                    PacketItem("pub_key", self_identity.export_public_key_bytes())
                ]
            )
        ))


        self.quit()
        LoginGUI()


    def create_title_bar(self) -> None:
        """
        Creates a custom title bar with the app logo.
        """
        green_frame = tk.Frame(self, bg = APP_MAIN_COLOR_DARK)
        green_frame.pack(fill = tk.X)
        title_frame = tk.Frame(green_frame, bg = APP_MAIN_COLOR_DARK)
        title_frame.pack(fill = tk.X, padx = 8)

        l1 = tk.Label(title_frame, image = self.image, border = 0)
        l1.pack(side = tk.LEFT)
        l2 = tk.Label(title_frame, text = "ChitChat", font = (APP_FONT, 30, "bold"), bg = APP_MAIN_COLOR_DARK, fg = APP_BG_COLOR)
        l2.pack(side = tk.RIGHT)

        ###
        green_frame.bind('<ButtonPress-1>', self.start_move)
        green_frame.bind('<ButtonRelease-1>', self.stop_move)
        green_frame.bind('<B1-Motion>', self.do_move)
        title_frame.bind('<ButtonPress-1>', self.start_move)
        title_frame.bind('<ButtonRelease-1>', self.stop_move)
        title_frame.bind('<B1-Motion>', self.do_move)
        l1.bind('<ButtonPress-1>', self.start_move)
        l1.bind('<ButtonRelease-1>', self.stop_move)
        l1.bind('<B1-Motion>', self.do_move)
        l2.bind('<ButtonPress-1>', self.start_move)
        l2.bind('<ButtonRelease-1>', self.stop_move)
        l2.bind('<B1-Motion>', self.do_move)
        ###


    def init_widgets(self) -> None:
        """
        Creates the widgets.
        """
        server_port_frame = tk.Frame(self, bg = APP_BG_COLOR)
        server_port_frame.grid_columnconfigure(0, weight = 2)
        server_port_frame.grid_columnconfigure(1, weight = 1)
        server_port_frame.pack(fill = tk.X, padx = 10, pady = 5)

        server_frame = tk.Frame(server_port_frame, bg = APP_BG_COLOR)
        server_frame.grid(row = 0, column = 0, sticky = "ew")
        tk.Label(server_frame, text = "Server", bg = APP_BG_COLOR, fg = APP_MAIN_COLOR, font = (APP_FONT, 12, "bold")).pack(pady = 3, anchor = "w")
        self.server: tk.Entry = tk.Entry(server_frame, selectbackground = APP_MAIN_COLOR,width = 40, background = APP_BG_COLOR_DARK, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.server.pack(fill = tk.X, padx = 3)

        port_frame = tk.Frame(server_port_frame, bg = APP_BG_COLOR)
        port_frame.grid(row = 0, column = 1, sticky = "ew")
        tk.Label(port_frame, text = "port", bg = APP_BG_COLOR, fg = APP_MAIN_COLOR, font = (APP_FONT, 12, "bold")).pack(pady = 3, anchor = "w")
        self.port: tk.Entry = tk.Entry(port_frame, selectbackground = APP_MAIN_COLOR,width = 20, background = APP_BG_COLOR_DARK, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.port.pack(fill = tk.X, padx = 3)

        self.error: tk.Label = tk.Label(self, text = "", fg = "#DF2C2C", bg = APP_BG_COLOR)
        self.error.pack(anchor = "w", padx = 10)

        buttons_frame = tk.Frame(self, bg = APP_BG_COLOR)
        buttons_frame.pack(side = tk.BOTTOM, fill = tk.BOTH, padx = 10, pady = 5)
        
        tk.Button(buttons_frame, text = "Connect", font = (APP_FONT, 12, "bold"), bg = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK, fg = APP_BG_COLOR, activeforeground = APP_BG_COLOR, border = 0, command = self.connect).pack(pady = 2, fill = tk.X)        

        t = tk.Frame(buttons_frame, bg = "#DF2C2C")
        t.pack(pady = 2, fill = tk.X)
        t.grid_rowconfigure(0, weight = 1)
        t.grid_columnconfigure(0, weight = 1)
        tk.Button(t, text = "Exit", font = (APP_FONT, 12, "bold"), bg = APP_BG_COLOR, activebackground = APP_BG_COLOR_DARK, fg = "#DF2C2C", activeforeground = "#DF2C2C", border = 0, command = self.quit).grid(row = 0, column = 0, sticky = "ew", padx = 1, pady = 1)

        


class LoginGUI(NoFrame):
    def __init__(self):
        NoFrame.__init__(self, "ChitChat - Login", LOGIN_SIZE, bg = APP_BG_COLOR)
        self.grid_rowconfigure(1, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        self.image: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open("sprites/icon.png"))

        self.create_title_bar()
        self.main_frame: tk.Frame = tk.Frame(self, bg = APP_BG_COLOR)
        self.main_frame.grid(row = 1, column = 0, sticky = "news")
        self.init_login_widgets()
    
        self.mainloop()


    def register(self) -> None:
        username = self.username.get()
        if len(username) == 0:
            self.error.config(text = "[Error] Please enter a username")
            return
        if self.password.get() != self.password2.get():
            self.error.config(text = "[Error] Passwords do not match")
            return
        if not is_secure(self.password.get()):
            self.error.config(text = "[Error] Bad password, must contain at least 12 characters, one uppercase character, one lower case character and one digit")
            return
        if len(username) == len(self.password.get()):
            self.error.config(text = "[Error] Usarname and password cannot be the same!")
            return
        p = Packet(
            [#TODO costanti
                PacketItem("register", (username, self.password.get()))
            ]
        )
        send_ciphered_message(p, s, server_identity)
        outcome = receive_ciphered_message(s, self_identity)
        if outcome[0].data:
            self.quit()
            LoggedGUI(username, int(outcome[1].data))
        else:
            self.error.config(text = outcome[1].data)


    
    def login(self) -> None:
        username = self.username.get()
        tag = int(self.tag.get())
        p = Packet(
            [#TODO costanti
                PacketItem("login", (username, tag, self.password.get()))
            ]
        )
        send_ciphered_message(p, s, server_identity)
        outcome = receive_ciphered_message(s, self_identity)
        if outcome[0].data:
            print("success")
        else:
            print("login error")
            return
        # if login success... TODO
        self.quit()
        LoggedGUI(username, tag)

    
    def create_title_bar(self) -> None:
        """
        Creates a custom title bar with the app logo.
        """
        green_frame = tk.Frame(self, bg = APP_MAIN_COLOR_DARK)
        green_frame.grid(row = 0, column = 0, sticky = "ew")
        title_frame = tk.Frame(green_frame, bg = APP_MAIN_COLOR_DARK)
        title_frame.pack(fill = tk.X, padx = 15)


        
        l1 = tk.Label(title_frame, image = self.image, border = 0)
        l1.pack(side = tk.LEFT)
        l2 = tk.Label(title_frame, text = "ChitChat", font = (APP_FONT, 38, "bold"), bg = APP_MAIN_COLOR_DARK, fg = APP_BG_COLOR)
        l2.pack(side = tk.RIGHT)

        ###
        green_frame.bind('<ButtonPress-1>', self.start_move)
        green_frame.bind('<ButtonRelease-1>', self.stop_move)
        green_frame.bind('<B1-Motion>', self.do_move)
        title_frame.bind('<ButtonPress-1>', self.start_move)
        title_frame.bind('<ButtonRelease-1>', self.stop_move)
        title_frame.bind('<B1-Motion>', self.do_move)
        l1.bind('<ButtonPress-1>', self.start_move)
        l1.bind('<ButtonRelease-1>', self.stop_move)
        l1.bind('<B1-Motion>', self.do_move)
        l2.bind('<ButtonPress-1>', self.start_move)
        l2.bind('<ButtonRelease-1>', self.stop_move)
        l2.bind('<B1-Motion>', self.do_move)
        ###
    
    def init_register_widgets(self) -> None:
        """
        Creates the register widgets.
        """
        # TODO: aggiungere font = APP_FONT dove manca in tutti i widget in questo file
        self.hidden_root.title("ChitChat - Register")

        for w in self.main_frame.winfo_children():
            w.destroy()


        tk.Label(self.main_frame, text = "Username", bg = APP_BG_COLOR, fg = APP_MAIN_COLOR, font = (APP_FONT, 12, "bold")).pack(anchor = "w", padx = 10)
        self.username: tk.Entry = tk.Entry(self.main_frame, selectbackground = APP_MAIN_COLOR,width = 0,background = APP_BG_COLOR_DARK, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.username.pack(fill = tk.X, padx = 10)

        tk.Label(self.main_frame, text = "Password", bg = APP_BG_COLOR, fg = APP_MAIN_COLOR, font = (APP_FONT, 12, "bold")).pack(anchor = "w", padx = 10)
        self.password: tk.Entry = tk.Entry(self.main_frame, selectbackground = APP_MAIN_COLOR,width = 0, show = '•',background = APP_BG_COLOR_DARK, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.password.pack(fill = tk.X, padx = 10)

        tk.Label(self.main_frame, text = "Confirm Password", bg = APP_BG_COLOR, fg = APP_MAIN_COLOR, font = (APP_FONT, 12, "bold")).pack(anchor = "w", padx = 10)
        self.password2: tk.Entry = tk.Entry(self.main_frame, selectbackground = APP_MAIN_COLOR,width = 0, show = '•',background = APP_BG_COLOR_DARK, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.password2.pack(fill = tk.X, padx = 10)


        self.error: tk.Label = tk.Label(self.main_frame, text = "", fg = "#DF2C2C", bg = APP_BG_COLOR, wraplength = 330, justify = tk.LEFT)
        self.error.pack(anchor = "w", padx = 10)

        buttons_frame = tk.Frame(self.main_frame, bg = APP_BG_COLOR)
        buttons_frame.pack(side = tk.BOTTOM, fill = tk.BOTH, padx = 10, pady = 5)
        
        tk.Button(buttons_frame, text = "Register", font = (APP_FONT, 12, "bold"), bg = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK, fg = APP_BG_COLOR, activeforeground = APP_BG_COLOR, border = 0, command = self.register).pack(pady = 2, fill = tk.X)
        
        t = tk.Frame(buttons_frame, bg = APP_MAIN_COLOR_DARK)
        t.pack(pady = 2, fill = tk.X)
        t.grid_rowconfigure(0, weight = 1)
        t.grid_columnconfigure(0, weight = 1)
        tk.Button(t, text = "Already a Member? Login", font = (APP_FONT, 12, "bold"), bg = APP_BG_COLOR, activebackground = APP_BG_COLOR_DARK, fg = APP_MAIN_COLOR, activeforeground = APP_MAIN_COLOR, border = 0, command = self.init_login_widgets).grid(row = 0, column = 0, sticky = "ew", padx = 1, pady = 1)
        
        t = tk.Frame(buttons_frame, bg = "#DF2C2C")
        t.pack(pady = 2, fill = tk.X)
        t.grid_rowconfigure(0, weight = 1)
        t.grid_columnconfigure(0, weight = 1)
        tk.Button(t, text = "Exit", font = (APP_FONT, 12, "bold"), bg = APP_BG_COLOR, activebackground = APP_BG_COLOR_DARK, fg = "#DF2C2C", activeforeground = "#DF2C2C", border = 0, command = self.quit).grid(row = 0, column = 0, sticky = "ew", padx = 1, pady = 1)
        
        


    def init_login_widgets(self) -> None:
        """
        Creates the login widgets.
        """
        # TODO: aggiungere font = APP_FONT dove manca in tutti i widget in questo file
        #for w in self.main_frame.winfo_children():
        #    w.destroy()
        self.hidden_root.title("ChitChat - Login")

        for w in self.main_frame.winfo_children():
            w.destroy()

        username_tag_frame = tk.Frame(self.main_frame, bg = APP_BG_COLOR)
        username_tag_frame.grid_columnconfigure(0, weight = 2)
        username_tag_frame.grid_columnconfigure(1, weight = 1)
        username_tag_frame.pack(fill = tk.X, padx = 10, pady = 15)

        username_frame = tk.Frame(username_tag_frame, bg = APP_BG_COLOR)
        username_frame.grid(row = 0, column = 0, sticky = "ew")
        tk.Label(username_frame, text = "Username", bg = APP_BG_COLOR, fg = APP_MAIN_COLOR, font = (APP_FONT, 12, "bold")).pack(pady = 3, anchor = "w")
        self.username: tk.Entry = tk.Entry(username_frame, selectbackground = APP_MAIN_COLOR,width = 40, background = APP_BG_COLOR_DARK, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.username.pack(fill = tk.X, padx = 3)

        tag_frame = tk.Frame(username_tag_frame, bg = APP_BG_COLOR)
        tag_frame.grid(row = 0, column = 1, sticky = "ew")
        tk.Label(tag_frame, text = "TAG", bg = APP_BG_COLOR, fg = APP_MAIN_COLOR, font = (APP_FONT, 12, "bold")).pack(pady = 3, anchor = "w")
        self.tag: tk.Entry = tk.Entry(tag_frame, selectbackground = APP_MAIN_COLOR,width = 20, background = APP_BG_COLOR_DARK, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.tag.pack(fill = tk.X, padx = 3)

        tk.Label(self.main_frame, text = "Password", bg = APP_BG_COLOR, fg = APP_MAIN_COLOR, font = (APP_FONT, 12, "bold")).pack(anchor = "w", padx = 10)
        self.password: tk.Entry = tk.Entry(self.main_frame, selectbackground = APP_MAIN_COLOR,width = 0, show = '•',background = APP_BG_COLOR_DARK, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.password.pack(fill = tk.X, padx = 10)


        self.error: tk.Label = tk.Label(self.main_frame, text = "", fg = "#DF2C2C", bg = APP_BG_COLOR)
        self.error.pack(anchor = "w", padx = 10)

        buttons_frame = tk.Frame(self.main_frame, bg = APP_BG_COLOR)
        buttons_frame.pack(side = tk.BOTTOM, fill = tk.BOTH, padx = 10, pady = 5)
        
        tk.Button(buttons_frame, text = "Login", font = (APP_FONT, 12, "bold"), bg = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK, fg = APP_BG_COLOR, activeforeground = APP_BG_COLOR, border = 0, command = self.login).pack(pady = 2, fill = tk.X)
        
        t = tk.Frame(buttons_frame, bg = APP_MAIN_COLOR_DARK)
        t.pack(pady = 2, fill = tk.X)
        t.grid_rowconfigure(0, weight = 1)
        t.grid_columnconfigure(0, weight = 1)
        tk.Button(t, text = "New Here? Register", font = (APP_FONT, 12, "bold"), bg = APP_BG_COLOR, activebackground = APP_BG_COLOR_DARK, fg = APP_MAIN_COLOR, activeforeground = APP_MAIN_COLOR, border = 0, command = self.init_register_widgets).grid(row = 0, column = 0, sticky = "ew", padx = 1, pady = 1)
        
        t = tk.Frame(buttons_frame, bg = "#DF2C2C")
        t.pack(pady = 2, fill = tk.X)
        t.grid_rowconfigure(0, weight = 1)
        t.grid_columnconfigure(0, weight = 1)
        tk.Button(t, text = "Exit", font = (APP_FONT, 12, "bold"), bg = APP_BG_COLOR, activebackground = APP_BG_COLOR_DARK, fg = "#DF2C2C", activeforeground = "#DF2C2C", border = 0, command = self.quit).grid(row = 0, column = 0, sticky = "ew", padx = 1, pady = 1)
        



def out_handler() -> None:
    """
    TODO
    """
    global s, server_identity, self_identity, out_packet

    #print("out handler thread started.")
    while True:
        out_packet.append(PacketItem("ping", data = datetime.datetime.now()))
        out_packet.append(PacketItem("msg_get", data = None)) # get unread messages
        num_items = len(out_packet.data)
        send_ciphered_message(out_packet, s, server_identity)
        if num_items != len(out_packet.data):
            print("***WARNING*** some packetitems were not sent, before", num_items, "now", len(out_packet.data))
        out_packet.clear()

        #print("ping:", datetime.datetime.now() - send_date)
        time.sleep(0.5)
    print("connection handler thread closed.")


def in_handler(gui: NoFrame) -> None:
    """
    TODO
    """
    global out_packet
    while True:
        msg = receive_ciphered_message(s, self_identity)
        reload_chat_previews = False
        for item in msg:
            if item.type == "pong": #TODO fare il match e aggiornare python TODO COSTANTI
                #case "pong":
                    gui.ping = round((datetime.datetime.now() - item.data).total_seconds() * 1000)
                    gui.status_label.config(text = STATUS_STRING[gui.status] + " - " + str(gui.ping) + "ms")
            
            
            elif item.type == "create_chat_success":#TODO costanti
                    if item.data[0] in gui.chats:
                        gui.chats[item.data[0]].update(chat_name = item.data[1], description = item.data[2], users = item.data[4])
                    else:
                        gui.chats[item.data[0]] = (Chat(item.data[0], item.data[1], item.data[2], item.data[3], users = item.data[4]))
                    gui.newchat_error.configure(text = "")
                    gui.close_new_chat_menu()
                    reload_chat_previews = True

            elif item.type == "msg":#TODO costanti TODO ordinare per data
                    reload_chat_previews = True
                    #print("received message", item.data)
                    msg = ChatMessage(number = item.data[1], author = (item.data[2], item.data[3]), date = item.data[4], content = item.data[5].decode("utf-8"))
                    if item.data[0] not in gui.chats:
                        gui.chats[item.data[0]] = Chat(item.data[0], "Loading...", "Loading...", datetime.datetime.now())
                        reload_chat_previews = True
                    gui.chats[item.data[0]].append_message(msg)
                    if gui.current_chat:
                        if item.data[0] == gui.current_chat.id:
                            MessageFrame(gui, msg)
                            # Fix scroll region and scroll to the bottom
                            for i in range(2): 
                                gui.messages_canvas.frame.update_idletasks()
                                gui.messages_canvas.on_canvas_configure(None)
                                gui.messages_canvas.canvas.yview("moveto", "1.0")
            
            elif item.type == "update_chats":#TODO costanti
                    missing_chats_ids = []
                    for chat_id in item.data:
                        if chat_id not in gui.chats:
                            missing_chats_ids.append(chat_id)
                    #print("missing chats:", missing_chats_ids)

                    out_packet.append(PacketItem("get_chats", missing_chats_ids))

                    deleted_chats_ids = []
                    for chat_id in gui.chats:
                        if chat_id not in item.data:
                            deleted_chats_ids.append(chat_id)
                    #print("chats where you are not in anymore:", deleted_chats_ids)

                    for chat_id in deleted_chats_ids:
                        gui.chats.pop(chat_id)
                    gui.load_chat_previews()
            
            elif item.type == "get_chat": #TODO costanti
                    #print("users:", item.data[4])
                    if item.data[0] in gui.chats:
                        gui.chats[item.data[0]].update(chat_name = item.data[1], description = item.data[2], users = item.data[4])
                    else:
                        gui.chats[item.data[0]] = (Chat(item.data[0], item.data[1], item.data[2], item.data[3], users = item.data[4]))
                    reload_chat_previews = True
            
            elif item.type == "create_chat_fail":
                    if not item.data[0]:
                        err = "Something went wrong"
                    else:
                        err = "User does not exist" #TODO per qualche motivo spunta solo U in item.data[0]
                    if gui.is_new_chat_menu_open:
                        print("chat create error", err)
                        gui.newchat_error.config(text = err)
        if reload_chat_previews:
            gui.load_chat_previews()
                    
                    





class LoggedGUI(NoFrame):
    def __init__(self, username: str, tag: int) -> None:
        NoFrame.__init__(self, "ChitChat", MIN_SIZE)
        self.minsize(*MIN_SIZE)
        # Account
        self.user_name: str = username
        self.tag: int = tag
        self.status: int = STATUS_ONLINE
        self.ping: int = 0
        
        self.chats: dict[Chat] = None
        self.current_chat: Chat = None
        self.is_new_chat_menu_open: bool = False

        #Graphical Elements
        self.status_label: tk.Label = None

        self.chats_canvas: ScrollableFrame = None
        self.messages_canvas: ScrollableFrame = None
        self.main_frame: tk.Frame = None
        self.app_title: tk.Frame = None
        self.entry: tk.Entry = None
        self.search_bar: tk.Entry = None

        self.newchat_frame: tk.Frame = None
        self.newchat_name: tk.Entry = None
        self.newchat_description: tk.Text = None
        self.newchat_user: tk.Entry = None
        self.newchat_tag: tk.Entry = None
        self.newchat_error: tk.Label = None
        
        self.load_chats()

        self.images: dict[ImageTk.PhotoImage] = {}
        self.load_images()
        

        self.init_widgets()
        Thread(target = in_handler, args = (self,), daemon = True).start()
        Thread(target = out_handler, daemon = True).start()
        self.load_chat_previews()
        self.load_message_frames()


        #self.bind("<Configure>", self.on_resize)

        #self.resizing = False
        self.bind("<Configure>", self.on_configure)

        self.mainloop()

    
    def on_configure(self, event: tk.Event) -> None:
        if self.current_chat and len(self.current_chat.messages) >= 100 and event.widget == self:
            time.sleep(1/(10**300))


    def on_resize(self, event: tk.Event) -> None:
        return
        print("new", self.messages_canvas.frame.winfo_width()/2)
        for msg_frame in self.messages_canvas.frame.winfo_children():
            msg_frame.text_label.config(wraplengt = int(self.messages_canvas.frame.winfo_width()/2))
        return
        self.update()


    def quit(self):
        print("saving chats")
        self.save_chats()
        NoFrame.quit(self)


    def toggle_fullscreen(self, position_reset: bool = True) -> None:
        """
        If the app is in fullscreen, resets it to its previous size and position, otherwise resizes it in fullscreen
        """
        if self.is_fullscreen():
            if position_reset:
                self.geometry('%dx%d+%d+%d' % (*self.old_size, *self.old_pos))
            else:
                self.geometry('%dx%d' % self.old_size)
            self.winfo_children()[1].winfo_children()[0].winfo_children()[2].config(image = self.images["dimension21"])
            return 

        self.old_pos = (self.winfo_x(), self.winfo_y())
        self.old_size = (self.winfo_width(), self.winfo_height())
        self.geometry('%dx%d+%d+%d' % (self.winfo_screenwidth(), self.winfo_screenheight(), 0, 0))
        self.winfo_children()[1].winfo_children()[0].winfo_children()[2].config(image = self.images["dimension1"])

        self.update()
        self.on_resize()



    def open_new_chat_menu(self) -> None:
        self.is_new_chat_menu_open = True
        for w in self.newchat_frame.winfo_children():
            w.destroy()
        tk.Label(self.newchat_frame, text = "Chat name", bg = "#F0F0F0", fg = APP_MAIN_COLOR, font = (APP_FONT, 9, "bold")).pack(anchor = "w", padx = 10)
        self.newchat_name = tk.Entry(self.newchat_frame, selectbackground = APP_MAIN_COLOR,background = APP_BG_COLOR, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.newchat_name.pack(anchor = "w", padx = 10, pady = 3, fill = tk.X)

        tk.Label(self.newchat_frame, text = "Chat Description", bg = "#F0F0F0", fg = APP_MAIN_COLOR, font = (APP_FONT, 9, "bold")).pack(anchor = "w", padx = 10)
        self.newchat_description = tk.Text(self.newchat_frame, selectbackground = APP_MAIN_COLOR, width = 0, height = 3, background = APP_BG_COLOR, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.newchat_description.pack(anchor = "w", padx = 10, pady = 3, fill = tk.X)

        user_tag_frame = tk.Frame(self.newchat_frame, bg = "#F0F0F0")
        user_tag_frame.grid_columnconfigure(0, weight = 2)
        user_tag_frame.grid_columnconfigure(1, weight = 1)
        user_tag_frame.pack(padx = 10, pady = 3, fill = tk.X)

        user_frame = tk.Frame(user_tag_frame, bg = "#F0F0F0")
        user_frame.grid(row = 0, column = 0, sticky = "news")
        tk.Label(user_frame, text = "User", bg = "#F0F0F0", fg = APP_MAIN_COLOR, font = (APP_FONT, 9, "bold")).pack(anchor = "w")
        self.newchat_user = tk.Entry(user_frame, selectbackground = APP_MAIN_COLOR,width = 17, background = APP_BG_COLOR, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.newchat_user.pack(anchor = "w", fill = tk.X)
        
        tk.Label(user_tag_frame, text = "", bg = "#F0F0F0").grid(row = 0, column = 1)

        tag_frame = tk.Frame(user_tag_frame, bg = "#F0F0F0")
        tag_frame.grid(row = 0, column = 2, sticky = "news")
        tk.Label(tag_frame, text = "TAG", bg = "#F0F0F0", fg = APP_MAIN_COLOR, font = (APP_FONT, 9, "bold")).pack(anchor = "w")
        self.newchat_tag = tk.Entry(tag_frame, selectbackground = APP_MAIN_COLOR,width = 8, background = APP_BG_COLOR, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.newchat_tag.pack(anchor = "w", fill = tk.X)
        

        self.newchat_error = tk.Label(self.newchat_frame, text = "", fg = "#DF2C2C",bg = "#F0F0F0", font = (APP_FONT, 9, "bold"))
        self.newchat_error.pack()

        tk.Frame(self.newchat_frame, bg = APP_MAIN_COLOR_DARK).pack(fill = tk.X) # horizontal separator
        tk.Button(self.newchat_frame, text = "Create chat", bg = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK, fg = APP_BG_COLOR, activeforeground = APP_BG_COLOR, border = 0, font = (APP_FONT, 9, "bold"), command = self.new_chat).pack(fill = tk.X)
        tk.Frame(self.newchat_frame, bg = APP_MAIN_COLOR_DARK).pack(fill = tk.X) # horizontal separator
        tk.Button(self.newchat_frame, text = "Cancel", bg = APP_BG_COLOR, activebackground = APP_BG_COLOR_DARK, fg = APP_MAIN_COLOR, activeforeground = APP_MAIN_COLOR, border = 0, font = (APP_FONT, 9, "bold"), command = self.close_new_chat_menu).pack(fill = tk.X)
        tk.Frame(self.newchat_frame, bg = APP_MAIN_COLOR_DARK).pack(fill = tk.X) # horizontal separator
    
    def close_new_chat_menu(self) -> None:
        self.is_new_chat_menu_open = False
        for w in self.newchat_frame.winfo_children():
            w.destroy()
        tk.Button(self.newchat_frame, text = "New Chat", bg = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK, fg = APP_BG_COLOR, activeforeground = APP_BG_COLOR, border = 0, font = (APP_FONT, 9, "bold"), command = self.open_new_chat_menu).pack(fill = tk.X)
        tk.Frame(self.newchat_frame, bg = APP_MAIN_COLOR_DARK).pack(fill = tk.X) # horizontal separator

    
    def new_chat(self) -> None:
        global out_packet

        #TODO costanti
        #print("sending request to create new chat")
        out_packet.append(PacketItem("create_chat", (self.newchat_name.get(), self.newchat_description.get(1.0, tk.END), [(self.newchat_user.get(), int(self.newchat_tag.get()))])  ))
    

    def send_message(self, event: tk.Event = None) -> None:
        global out_packet
        #TODO costanti TODO attenzione se current_chat è null
        msg = self.entry.get()
        self.entry.delete(0, tk.END)
        msg = msg.lstrip()
        if len(msg) == 0: return
        #print("sending message to chat", self.current_chat.id, '"', msg, '"')
        out_packet.append(PacketItem("msg_send", (self.current_chat.id, msg)))
    

    def set_status(self, status: int):
        self.status = status
        self.status_label.config(text = STATUS_STRING[self.status] + " - " + str(self.ping) +"ms")
        #print("sending request to set status to", STATUS_STRING[self.status])
        out_packet.append(PacketItem("set_status", status))


    def logout(self) -> None:
        p = Packet(
            [#TODO constants
                PacketItem("logout", None)
            ]
        )
        try:
            send_ciphered_message(p, s, server_identity)
        except: pass

        self.quit()
        ConnectGUI()


    def load_chats(self):
        global out_packet
        if not os.path.exists("chats.txt"):
            with open("chats.txt", "wb") as file:
                pickle.dump({}, file)
            self.chats = {}
        else:
            with open("chats.txt", "rb") as file:
                self.chats = pickle.load(file)
        
        out_packet.append(PacketItem("update_chats", None))
        #TODO quando arriva un messaggio per una chat che non ho crea la chat il locale

    

    def save_chats(self):
        with open("chats.txt", "wb") as file:
            pickle.dump(self.chats, file)


    def load_chat_previews(self) -> None:
        """
        Creates a chat preview in the side panel for every chat
        """
        self.chats_canvas.canvas.yview("moveto", "0.0")
        for w in self.chats_canvas.frame.winfo_children():
            w.destroy()
        for chat in self.chats.values():
            chat_preview = ChatPreview(self.chats_canvas.frame, self, chat)
            chat_preview.pack(fill = tk.X)
            tk.Frame(self.chats_canvas.frame, bg = APP_MAIN_COLOR_DARK).pack(fill = tk.X) # horizontal separator
        
        for i in range(2):
            self.chats_canvas.frame.update_idletasks()
            self.chats_canvas.on_canvas_configure(None)
        self.update()


    def load_message_frames(self) -> None:
        """
        Loads the messages of the current chat
        """
        if not self.current_chat: return
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
        
        self.update()
    
    
    def load_images(self) -> None:
        """
        Loads the buttons images.
        """  

        for filename in os.listdir("sprites/profile pics"):
            if filename.endswith(".png"):
                self.images[filename.replace(".png", "")] = ImageTk.PhotoImage(Image.open("sprites/profile pics/" + filename))

        for filename in os.listdir("sprites/buttons"):
            if filename.endswith(".png"):
                self.images[filename.replace(".png", "")] = ImageTk.PhotoImage(Image.open("sprites/buttons/" + filename))

        for filename in os.listdir("sprites/other"):
            if filename.endswith(".png"):
                self.images[filename.replace(".png", "")] = ImageTk.PhotoImage(Image.open("sprites/other/" + filename))



    def init_widgets(self) -> None:
        """
        Creates the window structure and main components
        """
        #TODO: Ci sono molti self. inutili

        # Create main container
        self.grid_columnconfigure(0, weight = 0)
        self.grid_columnconfigure(1, weight = 3)
        self.grid_rowconfigure(0, weight = 1)


        #* --- SIDE PANEL FRAME --- #
        side_panel_frame = tk.Frame(self, bg = APP_MAIN_COLOR)
        side_panel_frame.grid_rowconfigure(0, weight = 0)
        side_panel_frame.grid_rowconfigure(1, weight = 0)
        side_panel_frame.grid_rowconfigure(2, weight = 0)
        side_panel_frame.grid_rowconfigure(3, weight = 1)
        side_panel_frame.grid_columnconfigure(0, weight = 1)
        side_panel_frame.grid(row = 0, column = 0, sticky = "news")


        #** Profile frame
        profile_frame = tk.Frame(side_panel_frame, background = APP_MAIN_COLOR)
        profile_frame.grid_columnconfigure(0, weight= 0)
        profile_frame.grid_columnconfigure(1, weight=1)
        profile_frame.grid_rowconfigure(0, weight = 1)
        profile_frame.grid(row = 0, column = 0, sticky = "news")
        

        #*** Profile pic 
        profile_pic = tk.Menubutton(profile_frame, image = self.images["user"], border = 0, background = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK, width = 60, height = 60)
        profile_pic.menu = tk.Menu(profile_pic, tearoff = 0)
        profile_pic["menu"] = profile_pic.menu
        profile_pic.menu.add_cascade(label = "online", command = lambda: self.set_status( STATUS_ONLINE ), font = (APP_FONT, 9), activebackground = APP_MAIN_COLOR, activeforeground = APP_BG_COLOR)
        profile_pic.menu.add_cascade(label = "away", command = lambda: self.set_status( STATUS_AWAY ), font = (APP_FONT, 9), activebackground = APP_MAIN_COLOR, activeforeground = APP_BG_COLOR)
        profile_pic.menu.add_cascade(label = "busy", command = lambda: self.set_status(  STATUS_BUSY ), font = (APP_FONT, 9), activebackground = APP_MAIN_COLOR, activeforeground = APP_BG_COLOR)
        profile_pic.menu.add_cascade(label = "invisible", command = lambda: self.set_status( STATUS_INVISIBLE ), font = (APP_FONT, 9), activebackground = APP_MAIN_COLOR, activeforeground = APP_BG_COLOR)
        profile_pic.grid(row = 0, column = 0, sticky = "news")
        #*** Profile info frame
        profile_info_frame = tk.Frame(profile_frame, background = APP_MAIN_COLOR)
        profile_info_frame.grid_rowconfigure(0, weight = 0)
        profile_info_frame.grid_rowconfigure(1, weight = 1)
        profile_info_frame.grid_columnconfigure(0, weight = 1)
        profile_info_frame.grid(row = 0, column = 1, sticky = "news")

        #**** Username and buttons
        username_buttons_frame = tk.Frame(profile_info_frame, background = APP_MAIN_COLOR)
        username_buttons_frame.bind('<ButtonPress-1>', self.start_move)
        username_buttons_frame.bind('<ButtonRelease-1>', self.stop_move)
        username_buttons_frame.bind('<B1-Motion>', self.do_move)
        username_buttons_frame.grid(row = 0, column = 0, sticky = "news")

        username = tk.Label(username_buttons_frame, text = self.user_name + " #" + str(self.tag) + (' ' * (15 - len(self.user_name))), font = (APP_FONT, 12, "bold"), background = APP_MAIN_COLOR, fg = APP_BG_COLOR)
        username.pack(side = tk.LEFT)
        username.bind('<ButtonPress-1>', self.start_move)
        username.bind('<ButtonRelease-1>', self.stop_move)
        username.bind('<B1-Motion>', self.do_move)

        more_button = tk.Menubutton(username_buttons_frame, image = self.images["more"], border = 0, background = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK)
        more_button.menu = tk.Menu(more_button, tearoff = 0)
        more_button["menu"] = more_button.menu
        more_button.menu.add_cascade(label="Logout", command = self.logout, font = (APP_FONT, 9), activebackground = APP_MAIN_COLOR, activeforeground = APP_BG_COLOR)
        more_button.pack(side = tk.RIGHT, fill = tk.Y)

        settings_button = tk.Button(username_buttons_frame, image = self.images["settings"], border = 0, background = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK)
        settings_button.pack(side = tk.RIGHT, fill = tk.Y)

        #**** Status
        status_frame = tk.Frame(profile_info_frame, background = APP_MAIN_COLOR)
        status_frame.grid(row = 1, column=0, sticky = "news")
        self.status_label = tk.Label(status_frame, text = STATUS_STRING[self.status] + " - " + str(self.ping) +"ms", background = APP_MAIN_COLOR, fg = APP_BG_COLOR, font = (APP_FONT, 9))
        self.status_label.pack(side = tk.LEFT)


        #** Search bar frame
        sbar_frame = tk.Frame(side_panel_frame, background = APP_MAIN_COLOR_DARK)
        sbar_frame.grid(row = 1, column = 0, sticky = "news")
        tk.Label(sbar_frame, text = "Search Messages", background = APP_MAIN_COLOR_DARK, fg = APP_BG_COLOR, font = (APP_FONT, 9)).pack()
        self.search_bar = tk.Entry(sbar_frame, selectbackground = APP_MAIN_COLOR, border = 0, font = (APP_FONT, 9))
        self.search_bar.pack(fill = tk.X, padx = 5, pady = 5)
        
        self.search_bar.insert(0, "Coming soon!")
        self.search_bar.config(state = "disabled")
        


        # New chat frame
        self.newchat_frame = tk.Frame(side_panel_frame, bg = "#F0F0F0")
        self.newchat_frame.grid(row = 2, column = 0, sticky = "news")
        tk.Button(self.newchat_frame, text = "New Chat", bg = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK, fg = APP_BG_COLOR, activeforeground = APP_BG_COLOR, border = 0, font = (APP_FONT, 9, "bold"), command = self.open_new_chat_menu).pack(fill = tk.X)
        tk.Frame(self.newchat_frame, bg = APP_MAIN_COLOR_DARK).pack(fill = tk.X) # horizontal separator

        # Chats container
        self.chats_canvas = ScrollableFrame(side_panel_frame, bg = APP_MAIN_COLOR_DARK, separator_color = APP_MAIN_COLOR)
        self.chats_canvas.grid(row = 3, column = 0, sticky = "news")

        #tk.Label(self.side_panel_frame, text = "side panel").pack()

        #* --- MAIN FRAME --- #
        main_frame = tk.Frame(self, bg = APP_BG_COLOR)
        self.main_frame = main_frame #TODO
        main_frame.grid_rowconfigure(0, weight = 0)
        main_frame.grid_rowconfigure(1, weight = 0)
        main_frame.grid_rowconfigure(2, weight = 1)
        main_frame.grid_rowconfigure(3, weight = 0)
        main_frame.grid_rowconfigure(4, weight = 0)
        main_frame.grid_columnconfigure(0, weight = 1)
        main_frame.grid(row = 0, column = 1, sticky = "news")

        #** Title bar 
        titleBar = tk.Frame(main_frame, bg = APP_BG_COLOR)
        #*** Close button
        tk.Button(titleBar, image = self.images["close1"], border = 0, command = self.quit).pack(side = tk.RIGHT)
        tk.Frame(titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        #*** Resize button
        tk.Button(titleBar, image = self.images["dimension21"], border = 0, command = self.toggle_fullscreen).pack(side = tk.RIGHT)
        tk.Frame(titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        #*** Minimize button
        tk.Button(titleBar, image = self.images["minimize1"], border = 0, command = self.minimize).pack(side = tk.RIGHT)
        tk.Frame(titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        self.app_title = tk.Label(titleBar, text = self.title(), bg = APP_BG_COLOR, font = (APP_FONT, 9))
        self.app_title.pack(side = tk.LEFT)

        titleBar.grid(row = 0, column = 0, sticky = "news")
        self.app_title.bind('<ButtonPress-1>', self.start_move)
        self.app_title.bind('<ButtonRelease-1>', self.stop_move)
        self.app_title.bind('<B1-Motion>', self.do_move)
        titleBar.bind('<ButtonPress-1>', self.start_move)
        titleBar.bind('<ButtonRelease-1>', self.stop_move)
        titleBar.bind('<B1-Motion>', self.do_move)

        #** Horizonatal separator
        tk.Frame(main_frame, bg = APP_MAIN_COLOR).grid(row = 1, column = 0, sticky = "ew")

        #** Messages frame
        self.messages_canvas = ScrollableFrame(main_frame, bg = APP_BG_COLOR)
        self.messages_canvas.grid(row = 2, column = 0, sticky = "news")

        #** Horizonatal separator
        tk.Frame(main_frame, bg = APP_MAIN_COLOR).grid(row = 3, column = 0, sticky = "ew")

        #** Entry & send button
        entry_send = tk.Frame(main_frame, background = "#F0F0F0")
        entry_send.grid_columnconfigure(0, weight = 1)
        entry_send.grid_columnconfigure(1, weight = 0)
        entry_send.grid_columnconfigure(2, weight = 0)
        entry_send.grid_rowconfigure(0, weight = 1)
        entry_send.grid(row = 4, column = 0, sticky = "news")

        self.entry = tk.Entry(entry_send, selectbackground = APP_MAIN_COLOR,state = "disabled", background = APP_BG_COLOR, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = (APP_FONT, 12))
        self.entry.bind("<Return>", self.send_message)
        self.entry.grid(row = 0, column = 0, sticky = "news", padx = 15, pady = 5)
        tk.Button(entry_send, image = self.images["send"], border = 0, background = "#F0F0F0", command = self.send_message).grid(row = 0, column = 1, sticky = "news")
        s = Sizegrip(entry_send, style = "TSizegrip")
        s.grid(row = 0, column = 2, sticky="news")

        s.bind("<B1-Motion>", self.on_resize)

        #tk.Label(entry_send, text = "  ", background = APP_BG_COLOR).grid(row = 0, column = 2)
    






