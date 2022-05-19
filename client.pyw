import pygame, os
from GUI import *

#For window transparency
import win32api
import win32con
import win32gui

TRANSPARENT = (255, 0, 128)
FRAME_HEIGHT = None
BUTTONS_WIDTH = None
size = None
w = None
h = None
wn = None
font1 = None
sprites = {}



def init():
    global sprites, font1, size, w, h, wn, FRAME_HEIGHT, BUTTONS_WIDTH
    pygame.init()


    infoObject = pygame.display.Info()
    size = w, h = infoObject.current_w, infoObject.current_h

    FRAME_HEIGHT = round(h/30) #22.5
    BUTTONS_WIDTH = round(w/30)

    wn = pygame.display.set_mode(size, pygame.NOFRAME)


    # Create layered window
    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    # Set window transparency color
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*TRANSPARENT), 0, win32con.LWA_COLORKEY)

    pygame.font.init()
    font1 = pygame.font.SysFont("Arial", 20, 1)

    for filename in os.listdir("sprites"):
        if filename.endswith(".png"):
            sprites[filename.replace(".png","")] = pygame.image.load("sprites/" + filename).convert_alpha()

def main():
    init()
    clock = pygame.time.Clock()

    gui = Window(wn, 920, 640, "", font1, (249,249,249), (40,130,120), FRAME_HEIGHT, BUTTONS_WIDTH, sprites = sprites)
    #(15,20,25)
    while 1:
        mx,my = win32gui.GetCursorPos()
        mxr = mx - gui.x; myr = my-gui.y
        
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return


        ###########################
        if  not gui.step(mx, my, events): return
          
        wn.fill(TRANSPARENT)
        if gui.dragging:
            wn.set_at((int(mx),int(my)),(0,0,0))
        
        gui.draw(mx,my)

        ###########################

        pygame.display.update()
        clock.tick(60)

main()
quit()
