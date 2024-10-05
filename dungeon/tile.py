from constants import NO_VARIANT, HEIGHT
from pgzero.actor import Actor
import os

class Tile:
    def __init__(self, name:str, variant:int, pos:tuple):
        self.name = name
        self.variant = variant
        self.pos = pos
    def image(self):
        return f"tiles/{self.name}/variant_{self.variant}"

triggers ={
    "chest":"click",
    "door":"click"
}

class AnimatedTile(Tile):
    def __init__(self, name:str, variant:int, state:str, pos:tuple):
        self.state = state
        self.frame = 0
        self.no_frames = {s:len(os.listdir(f"images/tiles/{name}/variant_{variant}/{s}")) for s in os.listdir(f"images/tiles/{name}/variant_{variant}")}
        self.triger = triggers[name]
        if self.triger == "always":
            self.is_animating = True
        else:
            self.is_animating = False
        self.has_finished_animating = False
        super().__init__(name, variant, pos)
    def image(self):
        return f"tiles/{self.name}/variant_{self.variant}/{self.state}/{round(self.frame)}"
    def next_frame(self,frame_speed):
        if self.is_animating:
            if self.frame < self.no_frames[self.state] - 1:
                self.frame += frame_speed
            elif self.triger == "always":
                self.frame = 0   
            else:
                self.has_finished_animating = True
    
class Chest(AnimatedTile):
    def __init__(self, name:str, variant:int, x:int):
        self.bottom = HEIGHT - Actor("tiles/brick/variant_0").height
        super().__init__(name, variant, "opening", (x,self.bottom - Actor("tiles/chest/variant_0/opening/0").height/2))
    
    def sound_path(self):
        return f"chest/{self.variant}"

class Door(AnimatedTile):
    def sound_path(self):
        if self.variant:
            return "door/close"
        else:
            return "door/open"