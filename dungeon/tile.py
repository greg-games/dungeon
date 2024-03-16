from constants import NO_VARIANT, HEIGHT
from pgzero.actor import Actor

class Tile:
    def __init__(self, name:str, variant:int, pos:tuple):
        self.name = name
        self.variant = variant
        self.pos = pos
    def image(self):
        if self.variant == NO_VARIANT:
            return self.name
        return self.name+"/"+str(self.variant)

class Chest(Tile):
    def __init__(self, name:str, variant:int, x:int, is_open:bool):
        self.is_open = is_open
        self.bottom = HEIGHT - Actor("brick/0").height
        self.frame = 0
        super().__init__(name, variant, (x,self.bottom - Actor("chest/0/0").height/2))
    def image(self):
        return self.name+"/"+str(self.variant)+"/"+str(self.frame)