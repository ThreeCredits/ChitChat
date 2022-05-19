import pygame

ANCHOR_NULL = 0
ANCHOR_RIGHT = 1
ANCHOR_LEFT = 2
ANCHOR_TOP = 4
ANCHOR_BOTTOM = 8


LEFT_PANEL_WIDTH = 150


def colorSum(color1, color2):
    res = []
    for i in range(len(color1)):
        res.append((color1[i] + color2[i])%256)
    return tuple(res)


def paintSprite(surf, color):
    for i in range(surf.get_height()):
        for j in range(surf.get_width()):
            c = surf.get_at((j,i))
            nc = color if len(c) == 3 else (*color, c[3])
            surf.set_at((j,i), nc)


class ImgButton:
    def __init__(self, x, y, size, color, img = None, parent = None, anchor = ANCHOR_NULL):
        self.parent = parent
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.anchor = anchor
        self.img = img


    @property
    def absolutePosition(self):
        x = self.x
        y = self.y
        if not self.parent or self.anchor == ANCHOR_NULL: return (x,y)
        if self.anchor & ANCHOR_RIGHT:
            x = self.parent.x + self.parent.width-x
        elif self.anchor & ANCHOR_LEFT:
            x = self.parent.x + x
            
        if self.anchor & ANCHOR_BOTTOM:
            y = self.parent.height-y
        elif self.anchor & ANCHOR_TOP:
            y = self.parent.y + y
            
        return (x, y)

    def onTouch(self, mx, my):
        x,y = self.absolutePosition
        return mx >= x and mx <= x + self.size[0]  and  my >= y and my <= y + self.size[1]


    def draw(self, wn, state):
        c = self.color
        if state:
            c = colorSum(self.color,(-10,-10,-10))

        x, y = self.absolutePosition
        pygame.draw.rect(wn, c, (x, y, *self.size))
        if self.img:
            wn.blit(self.img,(x + self.size[0]/2 - self.img.get_width()/2, y + self.size[1]/2 - self.img.get_height()/2))
        
    


class Window:
    def __init__(self, wn, width, height, title, font,bgColor, color,  frameHeight, buttonsWidth,sprites = None):
        self.wn = wn
        self.sprites = sprites
        self.x = wn.get_width()/2 - width/2
        self.y = wn.get_height()/2 - height/2

        self.screen = pygame.Surface((width, height))
        self.screen.fill(bgColor)

        self.width = width
        self.height = height

        self.title = title
        self.font = font
        
        self.bgColor = bgColor
        self.setColor(color)
        self.frameHeight = frameHeight
        self.buttonsWidth = buttonsWidth

        self.dragging = False
        self.startX = 0
        self.startY = 0

        self.buttons = []
        for i in range(3):
            self.buttons.append(ImgButton((self.buttonsWidth)*(i+1)-1, 0, (self.buttonsWidth - 1, self.frameHeight-1), self.bgColor, img = sprites[list(sprites.keys())[i]], parent = self, anchor = ANCHOR_RIGHT|ANCHOR_TOP))
        self.buttonDown = None


    def setColor(self, color):
        self.color = color
        for sprite in self.sprites.values():
            paintSprite(sprite, color)

    def step(self, mx, my, events):
        if self.dragging and not self.buttonDown:
            self.x = self.startX + mx
            self.y = self.startY + my

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in self.buttons:
                    if b.onTouch(mx,my):
                        print("premuto")
                        self.buttonDown = b
                        continue
                        
                if mx >= self.x and mx <= self.x + self.width  and  my >= self.y and my <= self.y + self.frameHeight:
                    self.dragging = True
                    self.startX = self.x - mx
                    self.startY = self.y - my

            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
                if self.buttonDown:
                    if self.buttonDown.onTouch(mx,my):
                        if self.buttonDown is self.buttons[0]: return False

                    self.buttonDown = None


        return True
                    

    def draw(self, mx, my):
        title = self.font.render(self.title, True, self.bgColor)
        
        pygame.draw.rect(self.wn, self.color, (self.x, self.y, LEFT_PANEL_WIDTH, self.height))
        pygame.draw.rect(self.wn, self.bgColor, (self.x + LEFT_PANEL_WIDTH,self.y, self.width - LEFT_PANEL_WIDTH, self.frameHeight))
        pygame.draw.line(self.wn, self.bgColor, (self.x + 1, self.y + self.frameHeight - 1), (self.x + LEFT_PANEL_WIDTH, self.y + self.frameHeight - 1))
        pygame.draw.line(self.wn, self.color, (self.x + LEFT_PANEL_WIDTH, self.y + self.frameHeight - 1), (self.x + self.width - 2, self.y + self.frameHeight - 1))
        for i in range(3):
            pygame.draw.line(self.wn, self.color, (self.x + self.width - self.buttonsWidth*(i+1),self.y + 1),(self.x + self.width - self.buttonsWidth*(i+1), self.y + self.frameHeight))

        self.wn.blit(title, (self.x + 5, self.y + self.frameHeight/2 - title.get_height()/2))
        #Screen Drawing
        self.screen.fill(self.bgColor)
        pygame.draw.rect(self.screen, self.color, (0,0, LEFT_PANEL_WIDTH, self.height))

        self.wn.blit(self.screen,(self.x, self.y + self.frameHeight))
        for b in self.buttons:

            onTouch = 0
            if b.onTouch(mx, my):
                onTouch = 1

            b.draw(self.wn, onTouch)

