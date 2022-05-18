import pygame, os
from GUI import *

#For window transparency
import win32api
import win32con
import win32gui

TRANSPARENT = (255, 0, 128)

pygame.init()


infoObject = pygame.display.Info()
size = w, h = infoObject.current_w, infoObject.current_h

wn = pygame.display.set_mode(size, pygame.RESIZABLE|pygame.NOFRAME)


# Create layered window
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
# Set window transparency color
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*TRANSPARENT), 0, win32con.LWA_COLORKEY)

pygame.font.init()
font1 = pygame.font.SysFont("Arial", 16)

sprites = {}
for filename in os.listdir("sprites"):
    if filename.endswith(".png"):
        sprites[filename.replace(".png","")] = pygame.image.load("sprites/" + filename).convert_alpha()

def main():
    clock = pygame.time.Clock()

    gui = Window(wn, 500,300, "Test", font1, (255,255,255), (0,255,0),38, sprites = sprites)
    
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
        
        gui.draw()

        ###########################

        pygame.display.update()
        clock.tick(60)

main()
quit()
