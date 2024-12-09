from pgzero.actor import Actor

class Heart(Actor):
    def __init__(self):
        self.name = "heart"
        self.frame = 9
        self.frame_speed = 0.005
        self._goal_frame = 9
        super().__init__("ui/heart/9")
    
    def animate(self,dt):
        if round(self.frame) != self._goal_frame:
            if self.frame > self._goal_frame:
                self.frame -= self.frame_speed*dt
                if(self.frame < self._goal_frame):
                    self.frame = self._goal_frame
            else:
                self.frame += self.frame_speed*dt
                if(self.frame > self._goal_frame):
                    self.frame = self._goal_frame
            self.image = f"ui/heart/{round(self.frame)}"

    def change_state(self,state:int):
        self._goal_frame = state*3