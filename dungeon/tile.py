from constants import NO_VARIANT, HEIGHT
from pgzero.actor import Actor
import os

class Tile:
    def __init__(self, name:str, variant:int, pos:tuple = (0,0)):
        self.name = name
        self.variant = variant
        self.pos = pos
    def image(self):
        return f"tiles/{self.name}/variant_{self.variant}"

class TileAddon(Tile):
    def image(self):
        return f"tiles/addons/{self.name}/variant_{self.variant}"

triggers ={
    "chest":"click",
    "door":"click",
    "spikes":"always"
}

class AnimatedTile(Tile):
    def __init__(self, name:str, variant:int, state:str, pos:tuple):
        self.state = state
        self.frame = 0
        self.no_frames = self.no_frames(name, variant)
        self.triger = triggers[name]
        if self.triger == "always":
            self.is_animating = True
        else:
            self.is_animating = False
        self.has_finished_animating = False
        super().__init__(name, variant, pos)

    def no_frames(self, name, variant):
        return {s:len(os.listdir(f"images/tiles/{name}/variant_{variant}/{s}"))
                for s in os.listdir(f"images/tiles/{name}/variant_{variant}")}
    
    def image(self):
        return f"tiles/{self.name}/variant_{self.variant}/{self.state}/{round(self.frame)}"
    
    def next_frame(self,frame_speed):
        if self.is_animating:
            if self.frame + frame_speed < self.no_frames[self.state] - 1:
                self.frame += frame_speed
            elif self.triger == "always":
                self.frame = 0   
            else:
                self.has_finished_animating = True

class AnimatedTileAddon(AnimatedTile):
    def no_frames(self, name, variant):
        return {s:len(os.listdir(f"images/tiles/addons/{name}/variant_{variant}/{s}"))
                for s in os.listdir(f"images/tiles/addons/{name}/variant_{variant}")}
    
    def image(self):
        return f"tiles/addons/{self.name}/variant_{self.variant}/{self.state}/{round(self.frame)}"

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
        self.bottom = HEIGHT - Actor("tiles/brick/variant_0").height
        super().__init__(name, variant, "opening", (x,self.bottom - Actor("tiles/chest/variant_0/opening/0").height/2))
        self.loot_table = chest_loot_table[self.variant]

    def sound_path(self):
        return f"chest/{self.variant}"

class Door(AnimatedTile):
    def sound_path(self):
        if self.variant:
            return "door/close"
        else:
            return "door/open"