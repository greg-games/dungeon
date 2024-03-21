from pgzero.actor import Actor
from pgzero.rect import Rect
import os
from constants import IDLE, RUNNING_RIGHT, RUNNING_LEFT,SOUND_NOT_PLAYING, SOUND_WILL_BE_PLAYED

class Player(Actor):
    def __init__(self):
        self.all_sounds = {sound_name[:-4]:SOUND_NOT_PLAYING for sound_name in os.listdir(f"sounds/player")}
        self.state = IDLE
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
        if self.__frame > self.__no_frames[self.state] - 1:
            self.__frame = 0
        self.image = f"player/{self.state}/{round(self.__frame)}"
    
    def change_state(self,state):
        if self.state != state:
            self.state = state
            self.__frame = 0
            self.toggle_sound("running",[RUNNING_RIGHT,RUNNING_LEFT])

    def toggle_sound(self, sound_name:str, states:list):
        if(self.state in states):
            if self.all_sounds[sound_name] == SOUND_NOT_PLAYING:
                self.all_sounds[sound_name] = SOUND_WILL_BE_PLAYED
        else:
            self.all_sounds[sound_name] = SOUND_NOT_PLAYING
    
    def change_x(self,x):
        self.x = x
        self.hitbox.topleft = (self.x - self.hitbox.width/2, self.y - self.hitbox.height/2)

    def sound_path(self,sound):
        return f"player/{sound}"