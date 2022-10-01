import os
import tkinter as tk


from typing import Tuple, Any
import string

MIN_SIZE = (600, 400)
TITLE_BAR_HEIGHT = 40
APP_MAIN_COLOR = "#288278"
APP_BG_COLOR = "#F9F9F9"

root = None
hidden_root = None



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

        self.images = {}
        self.load_images()
        self.init_widgets()

        root = root
        root.bind("<Configure>", GUI.on_resize)
        self.old_pos = self.center(*size)
        self.old_size = size
        

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
            

    def center(self, width: int, height: int) -> Tuple[int, int]:
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
    def start_move(event: Any) -> None:
        root.x = event.x
        root.y = event.y

    @staticmethod
    def stop_move(event: Any) -> None:
        root.x = None
        root.y = None

    @staticmethod
    def do_move(event: Any) -> None:
        deltax = event.x - root.x
        deltay = event.y - root.y
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

    def toggle_fullscreen(self) -> None:
        """
        If the app is in fullscreen, resets it to its previous size and position, otherwise resizes it in fullscreen
        """
        global root
        if root.winfo_width() == root.winfo_screenwidth() and root.winfo_height() == root.winfo_screenheight():
            root.geometry('%dx%d+%d+%d' % (*self.old_size, *self.old_pos))
            return 

        self.old_pos = (root.winfo_x(), root.winfo_y())
        self.old_size = (root.winfo_width(), root.winfo_height())
        root.geometry('%dx%d+%d+%d' % (root.winfo_screenwidth(), root.winfo_screenheight(), 0, 0))


    def load_images(self) -> None:
        """
        Loads the buttons images.
        """
        for filename in os.listdir("sprites/buttons"):
            if filename.endswith(".png"):
                self.images[filename.replace(".png", "")] = tk.PhotoImage(file = "sprites/buttons/" + filename)


    def init_widgets(self) -> None:
        """
        Creates the window structure and main components
        """
        global root
        # Create main container
        self.main_container = tk.Frame(root)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=3)
        self.main_container.rowconfigure(0, weight = 1)
        self.main_container.pack(expand=True, fill = tk.BOTH)

        # Create side panel frame
        self.side_panel_frame = tk.Frame(self.main_container, bg = APP_MAIN_COLOR)
        self.side_panel_frame.grid(row = 0, column = 0, sticky = "news")

        #tk.Label(self.side_panel_frame, text = "side panel").pack()

        # Create main frame
        self.main_frame = tk.Frame(self.main_container, bg = APP_BG_COLOR)
        self.main_frame.grid(row = 0, column = 1, sticky = "news")

        # Title bar 
        self.titleBar = tk.Frame(self.main_frame, bg = APP_BG_COLOR)
        # Close button
        tk.Button(self.titleBar, image = self.images["close1"], border = 0, command = GUI.quit).pack(side = tk.RIGHT)
        tk.Frame(self.titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        # Resize button
        tk.Button(self.titleBar, image = self.images["dimension1"], border = 0, command = self.toggle_fullscreen).pack(side = tk.RIGHT)
        tk.Frame(self.titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        # Minimize button
        tk.Button(self.titleBar, image = self.images["minimize1"], border = 0, command = GUI.minimize).pack(side = tk.RIGHT)
        tk.Frame(self.titleBar, bg = APP_MAIN_COLOR).pack(side = tk.RIGHT, fill = tk.Y) # vertical separator

        t = tk.Label(self.titleBar, text = self.title, bg = APP_BG_COLOR)
        t.pack(side = tk.LEFT)

        self.titleBar.pack(fill = tk.BOTH)
        t.bind('<ButtonPress-1>', GUI.start_move)
        t.bind('<ButtonRelease-1>', GUI.stop_move)
        t.bind('<B1-Motion>', GUI.do_move)
        self.titleBar.bind('<ButtonPress-1>', GUI.start_move)
        self.titleBar.bind('<ButtonRelease-1>', GUI.stop_move)
        self.titleBar.bind('<B1-Motion>', GUI.do_move)

        # Horizonatal separator
        tk.Frame(self.main_frame, bg = APP_MAIN_COLOR).pack(fill = tk.BOTH)

        

        