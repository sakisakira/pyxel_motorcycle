import pyxel
from world import *

class Button:
    TextSize = [3, 5]
    ButtonSize = [13, 13]

    def __init__(self, x, y, lable):
        self.x0 = x
        self.y0 = y
        self.label = lable

    def show(self):
        pyxel.rect(self.x0, self.y0,
                   self.ButtonSize[0], self.ButtonSize[1],
                   14)
        xd = (self.ButtonSize[0] - self.TextSize[0]) / 2
        yd = (self.ButtonSize[1] - self.TextSize[1]) / 2
        pyxel.text(self.x0 + xd, self.y0 + yd, self.label, 1)

class Input:
    def __init__(self):
        self.init_buttons()
        self.a_pressed = False
        self.b_pressed = False

    def init_buttons(self):
        margin = 10
        x0 = margin
        y0 = world.screen_size.y - margin - Button.ButtonSize[1]
        self.button_b = Button(x0, y0, "B")
        x0 = world.screen_size.x - margin - Button.ButtonSize[0]
        self.button_a = Button(x0, y0, "A")
        
    def update(self):
        self.a_pressed = False
        self.b_pressed = False
        if (pyxel.btn(pyxel.GAMEPAD1_BUTTON_A) or
            pyxel.btn(pyxel.KEY_A)):
            self.a_pressed = True
        if (pyxel.btn(pyxel.GAMEPAD1_BUTTON_B) or
            pyxel.btn(pyxel.KEY_B)):
            self.b_pressed = True

    def show(self):
        self.button_a.show()
        self.button_b.show()

    def a_pressed(self):
        return self.a_pressed

    def b_pressed(self):
        return self.b_pressed
