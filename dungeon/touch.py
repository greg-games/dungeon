from pgzrun import run_mod
from pgzero.game import PGZeroGame
from constants import WIDTH, HEIGHT
from global_functions import move_mouse_hitbox
from button import buttons_on
import pgzrun
import pygame
import sys

pgzero_game = None
fingers = {}

def on_finger_down(event):
    x = event.x * WIDTH
    y = event.y * HEIGHT
    fingers[event.finger_id] = (x, y)
    move_mouse_hitbox((x,y))
    buttons_on("clicked")

def on_finger_up(event):
    pos = fingers.pop(event.finger_id, None)
    move_mouse_hitbox(pos)
    buttons_on("released")

def new_inject_global_handlers(self):
    self.handlers[pygame.QUIT] = lambda e: sys.exit(0)
    self.handlers[pygame.VIDEOEXPOSE] = lambda e: None

    user_key_down = self.handlers.get(pygame.KEYDOWN)
    user_key_up = self.handlers.get(pygame.KEYUP)

    def key_down(event):
        if event.key == pygame.K_q and \
                event.mod & (pygame.KMOD_CTRL | pygame.KMOD_META):
            sys.exit(0)
        self.keyboard._press(event.key)
        if user_key_down:
            return user_key_down(event)

    def key_up(event):
        self.keyboard._release(event.key)
        if user_key_up:
            return user_key_up(event)
        
    self.handlers[pygame.KEYDOWN] = key_down
    self.handlers[pygame.KEYUP] = key_up
    self.handlers[pygame.FINGERDOWN] = on_finger_down
    self.handlers[pygame.FINGERUP] = on_finger_up

def my_run_mod(mod, **kwargs):
    pgzero_game = PGZeroGame(mod, **kwargs)
    pgzero_game.inject_global_handlers = new_inject_global_handlers.__get__(pgzero_game, PGZeroGame)
    pgzero_game.run()

pgzrun.run_mod = my_run_mod