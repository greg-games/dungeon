from pgzero.actor import Actor
from pgzero.rect import Rect
import os
from constants import IDLE

class Player(Actor):
    def __init__(self):
        self.__state = IDLE
        self.__frame = 0
        self.__no_frames = [len(os.listdir(f"images/player/{a}")) for a in range(len(os.listdir(f"images/player")))]
        super().__init__("player/0/0")
        self.__hitbox_width = self.width + 27
        self.__hitbox_height = self.height
        self.hitbox = Rect(
            (self.x - self.__hitbox_width/2, self.y - self.__hitbox_height/2), 
            (self.__hitbox_width, self.__hitbox_height)
            )
    
    def animate(self,frame_speed):
        self.__frame += frame_speed
        if self.__frame > self.__no_frames[self.__state] - 1:
            self.__frame = 0
        self.image = f"player/{self.__state}/{round(self.__frame)}"
    
    def change_state(self,state):
        if self.__state != state:
            self.__state = state
            self.__frame = 0
    
    def change_x(self,x):
        self.x = x
        self.hitbox.topleft = (self.x - self.__hitbox_width/2, self.y - self.__hitbox_height/2)