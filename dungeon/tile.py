from constants import NO_VARIANT, HEIGHT
from pgzero.actor import Actor
import os

class Tile:
    def __init__(self, name:str, variant:int, pos:tuple):
        self.name = name
        self.variant = variant
        self.pos = pos
    def image(self):
        return f"{self.name}/{self.variant}"

triggers ={
    "chest":"click",
    "door":"click"
}

class AnimatedTile(Tile):
    def __init__(self, name:str, variant:int, pos:tuple):
        self.frame = 0
        self.no_frames = [len(os.listdir(f"images/{name}/{v}")) for v in range(len(os.listdir(f"images/{name}")))]
        self.triger = triggers[name]
        if self.triger == "always":
            self.is_animating = True
        else:
            self.is_animating = False
        self.has_finished_animating = False
        super().__init__(name, variant, pos)
    def image(self):
        return f"{self.name}/{self.variant}/{round(self.frame)}"
    def next_frame(self,frame_speed):
        if self.is_animating:
            if self.frame < self.no_frames[self.variant] - 1:
                self.frame += frame_speed
            elif self.triger == "always":
                self.frame = 0   
            else:
                self.has_finished_animating = True
    
class Chest(AnimatedTile):
    def __init__(self, name:str, variant:int, x:int):
        self.bottom = HEIGHT - Actor("brick/0").height
        super().__init__(name, variant, (x,self.bottom - Actor("chest/0/0").height/2))