from pgzero.actor import Actor
from pgzero.rect import Rect
from random import randrange
import os
from constants import SOUND_NOT_PLAYING, SOUND_WILL_BE_PLAYED
from pygame import transform

all_entities = []

class Entity(Actor):
    def __init__(self,name,variant):
        self.name = name
        self.variant = variant
        self.all_sounds = {sound_name[:-4]:SOUND_NOT_PLAYING for sound_name in os.listdir(f"sounds/{self.name}")}
        self.state = "idle"
        self.dir = "right"
        self.__no_frames = {a:len(os.listdir(f"images/{self.name}/{self.variant}/{a}")) for a in os.listdir(f"images/{self.name}/{self.variant}")}
        self.__frame = randrange(0,self.__no_frames["idle"])
        super().__init__(f"{self.name}/{self.variant}/idle/0")
        self.__hitbox_width = self.width + 27
        self.__hitbox_height = self.height
        self.hitbox = Rect(
            (self.x - self.__hitbox_width/2, self.y - self.__hitbox_height/2), 
            (self.__hitbox_width, self.__hitbox_height)
            )
        all_entities.append(self)

    def animate(self,frame_speed):
        self.__frame += frame_speed
        if self.__frame > self.__no_frames[self.state] - 1:
            self.__frame = 0
        self.image = f"{self.name}/{self.variant}/{self.state}/{round(self.__frame)}"
        if self.dir == "left":
            self._surf = transform.flip(self._surf, True, False) 
    
    def change_state(self,state,dir = None):
        if self.state != state:
            self.__frame = 0
            self.state = state
            if dir != None: self.dir = dir
            self.toggle_sound("running",["running"])

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
        return f"{self.name}/{sound}"

class Player(Entity):
    def __init__(self):
        super().__init__("player","variant_0")

class Enemy(Entity):
    def __init__(self,name,variant):
        self.name = name
        self.variant = variant
        super().__init__(name,variant)