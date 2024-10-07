from constants import NO_VARIANT, HEIGHT
from pgzero.actor import Actor
import os

class Tile(Actor):
    def __init__(self, name:str, variant:int, pos:tuple = (0,0)):
        self.name = name
        self.variant = variant
        super().__init__(f"tiles/{self.name}/variant_{self.variant}", pos)

triggers ={
    "chest":"click",
    "door":"click"
}

class AnimatedTile(Actor):
    def __init__(self, name:str, variant:int, state:str, pos:tuple = (0,0)):
        self.state = state
        self.frame = 0
        self.no_frames = {s:len(os.listdir(f"images/tiles/{name}/variant_{variant}/{s}")) for s in os.listdir(f"images/tiles/{name}/variant_{variant}")}
        self.triger = triggers[name]
        if self.triger == "always":
            self.is_animating = True
        else:
            self.is_animating = False
        self.has_finished_animating = False
        self.name = name
        self.variant = variant
        super().__init__(f"tiles/{self.name}/variant_{self.variant}/{self.state}/0", pos)
    
    def animate(self,frame_speed):
        if self.is_animating:
            if self.frame < self.no_frames[self.state] - 1:
                self.frame += frame_speed
            elif self.triger == "always":
                self.frame = 0   
            else:
                self.has_finished_animating = True
            self.image = f"tiles/{self.name}/variant_{self.variant}/{self.state}/{round(self.frame)}"

chest_loot_table = [
    {
        "coin":(3,5)
    },{
        "crystal_red":(-1,2),
        "coin":(4,6)
    },{
        "crystal_green":(0,3),
        "crystal_red":(1,3),
        "coin":(5,7)
    },{
        "crystal_violet":(1,2),
        "crystal_green":(1,3),
        "crystal_red":(2,4),
        "coin":(6,8)
    },
]

class Chest(AnimatedTile):
    def __init__(self, name:str, variant:int, x:int):
        super().__init__(name, variant, "opening", (x,0))
        self.bottom = HEIGHT - Actor("tiles/brick/variant_0").height
        self.loot_table = chest_loot_table[self.variant]
        self.star_bottom = self.bottom

    def sound_path(self):
        return f"chest/{self.variant}"

class Door(AnimatedTile):
    def sound_path(self):
        if self.variant:
            return "door/close"
        else:
            return "door/open"