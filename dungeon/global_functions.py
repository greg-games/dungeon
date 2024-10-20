import sys
from pgzero.rect import Rect

mouse_hitbox = Rect((0,0),(2, 2))
go_left = False
go_right = False
go_up = False
go_down = False

def iscolliding(object1,object2,distance = 0):
    return (object1.right + distance > object2.left and 
            object1.left - distance < object2.right and 
            object1.top - distance < object2.bottom and 
            object1.bottom + distance > object2.top)

def is_in_browser():
    return sys.platform == "emscripten"
    #return True #for debug purposes

def move_mouse_hitbox(pos):
    mouse_hitbox.left = pos[0]-1
    mouse_hitbox.top = pos[1]-1