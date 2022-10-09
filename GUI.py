import os
import tkinter as tk
from turtle import back



from typing import Tuple, Any
import string

MIN_SIZE = (600, 400)
TITLE_BAR_HEIGHT = 40
APP_MAIN_COLOR = "#288278"
APP_MAIN_COLOR_DARK = "#216B6B"
APP_BG_COLOR = "#F9F9F9"
APP_BG_COLOR_DARK = "#E8E8E8"

STATUS_OFFLINE = 0
STATUS_ONLINE = 1
STATUS_BUSY = 2
STATUS_AWAY = 3
STATUS_INVISIBLE = 4

STATUS_STRING = ["offline", "online", "busy", "away", "invisible"]



root = None
hidden_root = None
images = {}


class GUI:
    def __init__(self, title: string, size: Tuple[int, int]) -> None:
        global root, hidden_root
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
        self.user_name = "Bruno"
        self.status = STATUS_ONLINE

        GUI.load_images()
        self.init_widgets()

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
        print("start", event.x, event.y)
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
            root.winfo_children()[0].winfo_children()[1].winfo_children()[0].winfo_children()[2].config(image = images["dimension1"])
            return 

        root.old_pos = (root.winfo_x(), root.winfo_y())
        root.old_size = (root.winfo_width(), root.winfo_height())
        root.geometry('%dx%d+%d+%d' % (root.winfo_screenwidth(), root.winfo_screenheight(), 0, 0))
        root.winfo_children()[0].winfo_children()[1].winfo_children()[0].winfo_children()[2].config(image = images["dimension21"])

    @staticmethod
    def load_images() -> None:
        """
        Loads the buttons images.
        """
        global images
        for filename in os.listdir("sprites/profile pics"):
            if filename.endswith(".png"):
                images[filename.replace(".png", "")] = tk.PhotoImage(file = "sprites/profile pics/" + filename)
        for filename in os.listdir("sprites/buttons"):
            if filename.endswith(".png"):
                images[filename.replace(".png", "")] = tk.PhotoImage(file = "sprites/buttons/" + filename)


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
        c = tk.Button(profile_frame, image = images["testpic"], border = 0, background = APP_MAIN_COLOR, activebackground = APP_MAIN_COLOR_DARK, width = 60, height = 60)
        c.grid(row = 0, column = 0, sticky = "news")

        #**** Profile info frame
        profile_info_frame = tk.Frame(profile_frame, background = APP_MAIN_COLOR)
        profile_info_frame.grid_rowconfigure(0, weight = 70)
        profile_info_frame.grid_rowconfigure(1, weight = 100)
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
        chats_frame = tk.Frame(side_panel_frame, background = APP_MAIN_COLOR)
        chats_frame.grid(row = 1, column = 0, sticky = "news")





        #tk.Label(self.side_panel_frame, text = "side panel").pack()

        #* --- MAIN FRAME --- #
        main_frame = tk.Frame(self.main_container, bg = APP_BG_COLOR)
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
        self.resize_button = tk.Button(self.titleBar, image = images["dimension1"], border = 0, command = GUI.toggle_fullscreen).pack(side = tk.RIGHT)
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
        tk.Frame(main_frame, bg = APP_MAIN_COLOR).grid(row = 1, column = 0, sticky = "news")

        #** Chat frame
        chat_frame = tk.Frame(main_frame, background = APP_BG_COLOR)
        chat_frame.grid(row = 2, column = 0, sticky = "news")

        #** Horizonatal separator
        tk.Frame(main_frame, bg = APP_MAIN_COLOR).grid(row = 3, column = 0, sticky = "news")

        #** Entry & send button
        entry_send = tk.Frame(main_frame, background = APP_BG_COLOR)
        entry_send.grid_columnconfigure(0, weight = 1)
        entry_send.grid_columnconfigure(1, weight = 0)
        entry_send.grid_columnconfigure(2, weight = 0)
        entry_send.grid_rowconfigure(0, weight = 1)
        entry_send.grid(row = 4, column = 0, sticky = "news")

        self.entry = tk.Entry(entry_send, background = APP_BG_COLOR_DARK, border = 0, highlightthickness=1, highlightcolor = APP_MAIN_COLOR, highlightbackground= APP_MAIN_COLOR,font = ("Segoe UI", 12))
        self.entry.grid(row = 0, column = 0, sticky = "news", padx = 15, pady = 5)
        tk.Button(entry_send, image = images["send"], border = 0, background = APP_BG_COLOR).grid(row = 0, column = 1, sticky = "news")
        tk.Label(entry_send, text = "  ", background = APP_BG_COLOR).grid(row = 0, column = 2)


        

        
