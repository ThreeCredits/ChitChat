import sys
sys.path.append("../ChitChat")
import GUI

def NoFrame_constructor_test():
    gui = GUI.NoFrame("Test", (300, 300))
    assert gui.state() == "normal"
    assert gui.hidden_root.state() == "normal"
    assert gui.title() == "Test"
    assert gui.hidden_root.title() == "Test"
    
    #check centered
    gui.update()
    x = gui.winfo_screenwidth()/2 - gui.winfo_width()/2
    y = gui.winfo_screenheight()/2 - gui.winfo_height()/2
    assert gui.winfo_geometry() == "300x300+%d+%d" % (x, y)
    assert gui.old_pos == (x, y)


def NoFrame_minimize_test():
    gui = GUI.NoFrame("Test", (300, 300))
    gui.minimize()
    assert gui.hidden_root.state() == "iconic"


def NoFrame_on_focus_test():
    gui = GUI.NoFrame("Test", (300, 300))
    gui.on_focus(None)
    assert gui.hidden_root.state() != "iconic"


def NoFrame_is_fullscreen_test():
    gui = GUI.NoFrame("Test", (300, 300))
    gui.geometry("%dx%d" % (gui.winfo_screenwidth(), gui.winfo_screenheight()))
    gui.update()
    assert gui.is_fullscreen()
