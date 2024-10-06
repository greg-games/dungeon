from pgzero.actor import Actor
from pygame import Rect, surfarray
from global_functions import iscolliding

all_buttons = []
buttons_in = dict()
buttons_out = dict()

def color_surface(surface, red, green, blue):
    arr = surfarray.pixels3d(surface)
    arr[:,:,0] = red
    arr[:,:,1] = green
    arr[:,:,2] = blue

class Button(Actor):
    def __init__(self, name,
                 on_click:tuple = (None,None,None),
                 on_release:tuple = (None,None,None),
                 on_press:tuple = (None,None,None),
                 on_unpress:tuple = (None,None,None)):
        self._pressed = on_press[0]
        self._unpressed = on_unpress[0]
        self._clicked = on_click[0]
        self._released = on_release[0]
        buttons_in[name] = {"pressed":on_press[1],
                            "unpressed":on_unpress[1],
                            "clicked":on_click[1],
                            "released":on_release[1]}
        buttons_out[name] = {"pressed":on_press[2],
                             "unpressed":on_unpress[2],
                             "clicked":on_click[2],
                             "released":on_release[2]}
        self.mode = "unpressed"
        self.can_interact = True
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

    def on_release(self,input):
        if (self.mode != "unpressed" and self.can_interact):
            self.mode = "unpressed"
            self._orig_surf.set_alpha(255)
            if self._released != None:
                return self._released(input)

    def on_click(self,mouse_hitbox,input):
        if (iscolliding(mouse_hitbox, self.hitbox) and self.can_interact
            and self.mode != "pressed"):
            self.mode = "pressed"
            self._orig_surf.set_alpha(127)  
            if self._clicked != None:
                return self._clicked(input)

    def on_unpress(self,input):
        if (self.mode == "unpressed" and self._unpressed != None and self.can_interact):
            return self._unpressed(input)

    def on_press(self,input):
        if (self.mode == "pressed" and self._pressed != None and self.can_interact):
            return self._pressed(input)

    def disable(self):
        self.image = f"ui/buttons/{self.name}_disabled"
        self.can_interact = False

    def enable(self):
        self.image = f"ui/buttons/{self.name}"
        self.can_interact = True