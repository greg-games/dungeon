from pgzero.actor import Actor
from pygame import Rect, surfarray
from global_functions import *
from constants import *

all_buttons = []
buttons_in = dict()
buttons_out = dict()

def color_surface(surface, red, green, blue):
    arr = surfarray.pixels3d(surface)
    arr[:,:,0] = red
    arr[:,:,1] = green
    arr[:,:,2] = blue


def buttons_on(event):
    for button in all_buttons:
        if event == "pressed":
            button.on_press()
        elif event == "unpressed":
            button.on_unpress()
        elif event == "clicked":
            button.on_click(mouse_hitbox)
        elif event == "released":
            button.on_release(mouse_hitbox)

class Button(Actor):
    def __init__(self, name,
                 on_click = None,
                 on_release = None,
                 on_press = None,
                 on_unpress = None):
        self._pressed = on_press
        self._unpressed = on_unpress
        self._clicked = on_click
        self._released = on_release
        self.mode = "unpressed"
        self.can_interact = True
        self.is_visible = True
        self.name = name
        super().__init__(f"ui/buttons/{name}")
        background = self._orig_surf.copy()
        color_surface(background,200,200,200)
        self.background = Actor(f"ui/buttons/{name}")
        self.background._orig_surf = background
        self.__hitbox_width = self.width
        self.__hitbox_height = self.height
        self.hitbox = Rect(
            (self.x - self.__hitbox_width/2, self.y - self.__hitbox_height/2), 
            (self.__hitbox_width, self.__hitbox_height)
            )
        all_buttons.append(self)

    def set_pos(self, pos):
        self.pos = pos
        self.hitbox.center = pos
        self.background.pos = pos

    def on_release(self,mouse_hitbox):
        if (iscolliding(mouse_hitbox, self.hitbox) and self.can_interact
            and self.mode != "unpressed"):
            self.mode = "unpressed"
            self._orig_surf.set_alpha(255)
            if self._released != None:
                self._released()

    def on_click(self,mouse_hitbox):
        if (iscolliding(mouse_hitbox, self.hitbox) and self.can_interact
            and self.mode != "pressed"):
            self.mode = "pressed"
            self._orig_surf.set_alpha(127)  
            if self._clicked != None:
                self._clicked()

    def on_unpress(self,):
        if (self.mode == "unpressed" and self._unpressed != None and self.can_interact):
            self._unpressed()

    def on_press(self,):
        if (self.mode == "pressed" and self._pressed != None and self.can_interact):
            self._pressed()

    def disable(self):
        self.image = f"ui/buttons/{self.name}_disabled"
        self.can_interact = False

    def enable(self):
        self.image = f"ui/buttons/{self.name}"
        self.can_interact = True
    
    def hide(self):
        self.is_visible = False
        self.can_interact = False

    def show(self):
        self.is_visible = True
        self.can_interact = True