import pygame

# Anchor constants
ANCHOR_NULL = 0
ANCHOR_RIGHT = 1
ANCHOR_LEFT = 2
ANCHOR_TOP = 4
ANCHOR_BOTTOM = 8


LEFT_PANEL_WIDTH = 150


def colorSum(color1, color2):
    """
    A function that, given 2 colors, returns the sum of their components.
    :param color1: The first color (r,g,b,[a])
    :param color2: The second color (r,g,b,[a])
    :returns: A color (tuple)
    """
    res = []
    for i in range(len(color1)):
        res.append((color1[i] + color2[i])%256)
    return tuple(res)


def paintSprite(surf, color):
    """
    A function that, given a reference to a surface and a color, paints all the pixels of the surface with that color.
    It will be used to paint the buttons icons when the theme is changed.
    :param surf: A reference to the surface to draw on.
    :param color: A tuple representing the desired color.
    :returns: None.
    """
    for i in range(surf.get_height()):
        for j in range(surf.get_width()):
            c = surf.get_at((j,i))
            nc = color if len(c) == 3 else (*color, c[3])
            surf.set_at((j,i), nc)


class ImgButton: 
    """
    A class representing a rectangular button with an image inside.
    """
    def __init__(self, x, y, size, color, img = None, parent = None, anchor = ANCHOR_NULL):
        self.parent = parent    # A reference to any instance that has a "x" and "y" attribute
        self.x = x; self.y = y  # x&y coordinates relative to the parent 
        self.size = size        # A 2-uple that contains the width and height of the button
        self.color = color      # It's used as background color for the button
        self.anchor = anchor    # A mask representing the anchor relative to the given parent
        self.img = img          # A reference to the surface to draw inside the button


    @property
    def absolutePosition(self):
        """
        This method is used to get the button position relative to the screen.
        :returns: A 2-uple with the absolute position of the button.
        """
        x = self.x
        y = self.y
        if not self.parent or self.anchor == ANCHOR_NULL: return (x,y) # if there is no parent or anchor then the button position is already absolute.
        # Now we differenciate the orizontal anchor
        if self.anchor & ANCHOR_RIGHT:
            x = self.parent.x + self.parent.width-x
        elif self.anchor & ANCHOR_LEFT:
            x = self.parent.x + x

        # Same as above but for vertical anchor
        if self.anchor & ANCHOR_BOTTOM:
            y = self.parent.height-y
        elif self.anchor & ANCHOR_TOP:
            y = self.parent.y + y
            
        return (x, y)

    def onTouch(self, mx, my):
        """
        This method is used to check if the cursor is colliding with the button.
        :param mx: The absolute cursor x position.
        :param my: The absolute cursor y position.
        :returns: A boolean representing whether the button is being touched by the cursor or not.
        """
        x,y = self.absolutePosition
        return mx >= x and mx <= x + self.size[0]  and  my >= y and my <= y + self.size[1]


    def draw(self, wn, state):
        """
        This method renders the button on a given surface using its coordinates.
        :param wn: A reference to the surface where the button will be drawn.
        :param state: A boolean representing whether the button is being touched by the cursor or not.
        """
        c = self.color
        # If the button is being hovered on, its color will be darker
        # TODO: Variable hover color 
        if state:
            c = colorSum(self.color,(-10,-10,-10))

        # We want to use the absolute button position, because we are drawing it directly on the screen
        x, y = self.absolutePosition
        pygame.draw.rect(wn, c, (x, y, *self.size))
        if self.img:
            wn.blit(self.img,(x + self.size[0]/2 - self.img.get_width()/2, y + self.size[1]/2 - self.img.get_height()/2))
        
    


class Window:
    """
    The Window class represents a frameless window that will be drawn on the main transparent window.
    """
    def __init__(self, wn, width, height, title, font,bgColor, color,  frameHeight, buttonsWidth,sprites = None):
        self.wn = wn                                    # A reference to the pygame window where the window will be drawn
        self.sprites = sprites                          # A dictionary containing surfaces indexed by their name
        self.x = wn.get_width()/2 - width/2             # The window coordinates(it starts at the center of the screen)
        self.y = wn.get_height()/2 - height/2

        self.screen = pygame.Surface((width, height))   # The window surface           

        self.width = width                              # The window size
        self.height = height

        self.title = title                              # The window title
        self.font = font                                # The window font
        
        self.bgColor = bgColor                          # The background color
        self.color = None                               # The window main color
        self.setColor(color)                            # Sets the window color
        self.frameHeight = frameHeight                  # The upper frame height
        self.buttonsWidth = buttonsWidth                # The width of the upper-right buttons

        self.dragging = False                           # A boolean that indicates if the window is being dragged
        self.startX = 0                                 # The relative position of the window to the mouse, when the drag starts
        self.startY = 0

        # Generating the upper-right buttons
        self.buttons = []
        for i in range(3):
            self.buttons.append(ImgButton((self.buttonsWidth)*(i+1)-1, 0, (self.buttonsWidth - 1, self.frameHeight-1), self.bgColor, img = sprites[list(sprites.keys())[i]], parent = self, anchor = ANCHOR_RIGHT|ANCHOR_TOP))
        self.buttonDown = None                          # A reference to the last button pressed (becomes None when a button is released)


    def setColor(self, color):
        """
        This method is used to change the window main color.
        :param color: a tuple representing the desired color.
        :returns: None.
        """
        self.color = color
        for sprite in self.sprites.values():
            paintSprite(sprite, color)

    def step(self, mx, my, events):
        """
        This method updates the window state.
        :param mx: The absolute cursor x position.
        :param my: The absolute cursor y position.
        :param events: A list of pygame events.
        :returns: A boolean that represents if the window has been closed.
        """

        # If the window is being dragged it will follow the cursor, only if there is no button pressed
        if self.dragging and not self.buttonDown:
            self.x = self.startX + mx
            self.y = self.startY + my

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in self.buttons:
                    if b.onTouch(mx,my):
                        self.buttonDown = b # We store that this button is being pressed
                        break               # We break from the loop because there cannot be more than one button pressed at the same time.
                
                # Checking if the window is being dragged by its frame
                if mx >= self.x and mx <= self.x + self.width  and  my >= self.y and my <= self.y + self.frameHeight:
                    self.dragging = True
                    self.startX = self.x - mx
                    self.startY = self.y - my

            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False # Window drag ends
                # If the cursor still hovers on the button, it will trigger its functionality
                if self.buttonDown:
                    if self.buttonDown.onTouch(mx,my):
                        if self.buttonDown is self.buttons[0]: return False

                    self.buttonDown = None


        return True
                    

    def draw(self, mx, my):
        """
        This method draws the window on the screen.
        :param mx: The absolute cursor x position.
        :param my: The absolute cursor y position.
        :returns: None.
        """
        title = self.font.render(self.title, True, self.bgColor) # rendering the title text
        
        # Drawing the upper frame
        pygame.draw.rect(self.wn, self.color, (self.x, self.y, LEFT_PANEL_WIDTH, self.height))
        pygame.draw.rect(self.wn, self.bgColor, (self.x + LEFT_PANEL_WIDTH,self.y, self.width - LEFT_PANEL_WIDTH, self.frameHeight))
        pygame.draw.line(self.wn, self.bgColor, (self.x + 1, self.y + self.frameHeight - 1), (self.x + LEFT_PANEL_WIDTH, self.y + self.frameHeight - 1))
        pygame.draw.line(self.wn, self.color, (self.x + LEFT_PANEL_WIDTH, self.y + self.frameHeight - 1), (self.x + self.width - 2, self.y + self.frameHeight - 1))
        for i in range(3):
            pygame.draw.line(self.wn, self.color, (self.x + self.width - self.buttonsWidth*(i+1),self.y + 1),(self.x + self.width - self.buttonsWidth*(i+1), self.y + self.frameHeight))

        self.wn.blit(title, (self.x + 5, self.y + self.frameHeight/2 - title.get_height()/2))
        
        # Drawing the window content
        self.screen.fill(self.bgColor)
        pygame.draw.rect(self.screen, self.color, (0,0, LEFT_PANEL_WIDTH, self.height))

        # Drawing the window on the screen
        self.wn.blit(self.screen,(self.x, self.y + self.frameHeight))

        # Drawing the buttons
        for b in self.buttons:
            # If the cursor is hovering the button we will pass it as argument
            onTouch = 0
            if b.onTouch(mx, my):
                onTouch = 1
            b.draw(self.wn, onTouch)

