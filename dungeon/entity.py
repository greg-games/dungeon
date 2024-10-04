from pgzero.actor import Actor
from pgzero.rect import Rect
from random import randrange
import os
from constants import LEFT, RIGHT, SOUND_NOT_PLAYING, SOUND_WILL_BE_PLAYED, WIDTH
from global_functions import iscolliding, is_in_browser
from pygame import transform

all_entities = []
all_sprites = []

ENTITY_FRAME_SPEED = 0.2

if is_in_browser():
    ENTITY_FRAME_SPEED = 0.5

#@staticmethod
def update_all_sprites(new_all_sprites):
    global all_sprites
    all_sprites = new_all_sprites

class Entity(Actor):
    def __init__(self,name,variant,running_speed,health, hitbox_width = 1, hitbox_height = 1, hitbox_offset = 0, **kwargs):
        self.name = name
        self.variant = variant
        self.all_sounds = {sound_name[:-4]:SOUND_NOT_PLAYING for sound_name in os.listdir(f"sounds/{self.name}")}
        self.state = "idle"
        self.health = health
        self.dir = RIGHT
        self.speed = 0
        self.running_speed = running_speed
        self.colliding = []
        self.attacking = []
        self.is_dead = False
        self._no_frames = {a:len(os.listdir(f"images/{self.name}/{self.variant}/{a}")) for a in os.listdir(f"images/{self.name}/{self.variant}")}
        self.frame_speed = {a:ENTITY_FRAME_SPEED for a in os.listdir(f"images/{self.name}/{self.variant}")}
        self.frame = randrange(0,self._no_frames["idle"])
        super().__init__(f"{self.name}/{self.variant}/idle/0")
        self._hitbox_width = self.width * hitbox_width
        self._hitbox_height = self.height * hitbox_height
        self.hitbox_offset = hitbox_offset * self._hitbox_width
        for key, value in kwargs.items():
            if key in self.frame_speed.keys():
                self.frame_speed[key] *= value
        self.hitbox = Rect(
            (self.x - self._hitbox_width/2, self.y - self._hitbox_height/2), 
            (self._hitbox_width, self._hitbox_height))
        self.attack_hitbox =  self.hitbox.copy()
        all_entities.append(self)

    def animate(self):
        self.frame += self.frame_speed[self.state]
        if self.frame > self._no_frames[self.state] - 1:
            self.frame = 0
            if self.state == "die":
                self.is_dead = True
                all_entities.remove(self)
                return
        self.image = f"{self.name}/{self.variant}/{self.state}/{round(self.frame)}"
        if self.dir == LEFT:
            self._orig_surf = transform.flip(self._orig_surf, True, False) 

    def change_state(self,state,dir = None):
        if dir != None: self.dir = dir
        if self.state != state:
            self.frame = 0
            self.state = state
            self.toggle_sound("running",["running"])
            if state == "hit":
                self.health -= 1
                if self.health <= 0:
                    self.change_state("die")

    def toggle_sound(self, sound_name:str, states:list):
        if(self.state in states):
            if self.all_sounds[sound_name] == SOUND_NOT_PLAYING:
                self.all_sounds[sound_name] = SOUND_WILL_BE_PLAYED
        else:
            self.all_sounds[sound_name] = SOUND_NOT_PLAYING

    def change_x(self,x):
        self.x = x
        self.hitbox.topleft = (self.x - self.hitbox.width/2 + self.hitbox_offset*self.dir,
                                self.y - self.hitbox.height/2)
        self.attack_hitbox.topleft = (self.x - self.hitbox.width*(0.5 - self.dir) + self.hitbox_offset*self.dir,
                                       self.y - self.hitbox.height/2)

    def update_colliding(self):
        self.colliding = []
        self.attacking = []
        for sprite in all_sprites:
            if(sprite.name != "background" and sprite != self):
                if hasattr(sprite,"hitbox"):
                    if(iscolliding(self.hitbox,sprite.hitbox,0)):
                        self.colliding.append(sprite)
                    if(iscolliding(self.attack_hitbox,sprite.hitbox,0)):
                        self.attacking.append(sprite)
                else:
                    if(iscolliding(self.hitbox,sprite,0)):
                        self.colliding.append(sprite)
                    if(iscolliding(self.attack_hitbox,sprite,0)):
                        self.attacking.append(sprite)

    def islookingat(self,object):
        return (object.x-self.x)*self.dir >= 0

    def move(self):
        self.change_x(self.x + self.speed*self.dir)
        if(self.speed == 0):
            self.change_state("idle")
        else:
            self.change_state("running",self.dir)

    def sound_path(self,sound):
        return f"{self.name}/{sound}"

class Player(Entity):
    def __init__(self):
        super().__init__("player","variant_0",WIDTH//120 - 0.5,5, hitbox_width = 1/5, hitbox_offset = -1/5,
                         duck = 0.4, idle = 0.6, running = 1.1, hit = 0.075)

    def update_hitbox(self):
        if self.state == "jump":
            self.hitbox.height =self._hitbox_height*3/5
            self.hitbox.top = self.top
        elif self.state == "duck":
            self.hitbox.height = self._hitbox_height/3
            self.hitbox.bottom = self.bottom
        else:
            self.hitbox.height = self._hitbox_height
            self.hitbox.bottom = self.bottom

    def move(self):
        self.update_hitbox()
        if(self.state == "idle" or self.state == "running"):
            super().move()

    def change_x(self,x):
        super().change_x(x)
        self.update_hitbox()

    def animate(self):
        if(self.frame + self.frame_speed[self.state] > self._no_frames[self.state] - 1):
            if self.state == "die":
                self.is_dead = True
                return
            if(self.speed == 0):
                self.change_state("idle")
            else:
                self.change_state("running",self.dir)
        super().animate()
        super().update_colliding()
        if(self.state == "attack1"and
            (round(self.frame) >= self._no_frames[self.state]-3)):
            for object in self.attacking:
                if object.name == "skeleton" and object.state == "idle":
                    object.change_state("hit")

class Enemy(Entity):
    def __init__(self,name,variant):
        self.name = name
        self.variant = variant
        super().__init__(name,variant,WIDTH//240,3, hitbox_offset = -1/3,
                         idle = 1.1, attack1 = 0.75, attack2 = 0.75, hit = 0.75, hitbox_width = 1/2)

    def go_to_player(self,player_x):
        self.speed = self.running_speed
        if self.x > player_x:
            self.dir = LEFT
        else:
            self.dir = RIGHT
    
    def change_state(self,state,dir = None):
        if state != self.state:
            if(state == "attack1" or state == "attack2"):
                if state == "attack1":
                    self.attack_hitbox.height = self._hitbox_height/3
                    self.attack_hitbox.top = self.top + self._hitbox_height/6
                else:
                    self.attack_hitbox.height = self._hitbox_height/3
                    self.attack_hitbox.bottom = self.bottom - self._hitbox_height/6
            else:
                self.attack_hitbox.height = self._hitbox_height
                self.attack_hitbox.bottom = self.bottom
        super().change_state(state, dir)
    
    def animate(self):
        super().animate()
        super().update_colliding()
        if((self.state == "attack1" or self.state == "attack2")and
            (round(self.frame) >= self._no_frames[self.state]-3)):
            for object in self.attacking:
                if object.name == "player":
                    object.change_state("hit")
                    self.change_state("idle")
                    super().animate()