from pgzero.actor import Actor
from global_functions import is_in_browser

class Loot(Actor):
    def __init__(self,name,pos):
        self.name = name
        super().__init__(f"loot/{self.name}",pos)
        self._orig_surf.set_alpha(0)  
        self.raise_height = 100
        no_frames = 20
        self.step = self.raise_height/no_frames
        self.end_y = self.y - self.raise_height

    def is_animating_finished(self, dt): 
        self._orig_surf.set_alpha(255)
        if self.y > self.end_y:
            self.y -= self.step*dt/10
            return False
        else:
            return True