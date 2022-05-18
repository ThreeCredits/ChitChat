import pygame

ANCHOR_NULL = 0
ANCHOR_RIGHT = 1
ANCHOR_LEFT = 2
ANCHOR_TOP = 4
ANCHOR_BOTTOM = 8

FRAME_BUTTONS_SIZE = 58


def colorSum(color1, color2):
    res = []
    for i in range(len(color1)):
        res.append((color1[i] + color2[i])%256)
    return tuple(res)


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

    def isPressed(self, mx, my):
        x,y = self.absolutePosition
        return mx >= x and mx <= x + self.size[0]  and  my >= y and my <= y + self.size[1]

    def draw(self, wn, state):
        c = self.color
        if state == 1:
            c = colorSum(self.color,(10,10,10))
        elif state == 2:
            c = colorSum(self.color, (-10,-10,-10))
        x, y = self.absolutePosition
        pygame.draw.rect(wn, self.color, (x, y, *self.size))
        if self.img:
            wn.blit(self.img,(x + self.size[0]/2 - self.img.get_width()/2, y + self.size[1]/2 - self.img.get_height()/2))
        
    


class Window:
    def __init__(self, wn, width, height, title, font,bgColor, frameColor,  frameHeight, sprites = None):
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
        self.frameColor = frameColor
        self.frameHeight = frameHeight

        self.dragging = False
        self.startX = 0
        self.startY = 0

        self.buttons = [ImgButton(FRAME_BUTTONS_SIZE, 0, (FRAME_BUTTONS_SIZE, self.frameHeight),(232,17,35),img = sprites["closeIcon"], parent = self, anchor = ANCHOR_RIGHT|ANCHOR_TOP)]
        self.buttonDown = None

    def step(self, mx, my, events):
        if self.dragging:
            self.x = self.startX + mx
            self.y = self.startY + my

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for b in self.buttons:
                    if b.isPressed(mx,my):
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
                    if self.buttonDown.isPressed(mx,my):
                        if self.buttonDown is self.buttons[0]: return False

                    self.buttonDown = None


        return True
                    

    def draw(self):
        pygame.draw.rect(self.wn, self.frameColor, (self.x, self.y, self.width, self.frameHeight))
        self.wn.blit(self.screen,(self.x, self.y + self.frameHeight))
        for b in self.buttons:
            b.draw(self.wn, 0)
        return b.absolutePosition
