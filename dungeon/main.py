import sys
import pgzrun
import asyncio

from random import *
from addon import Addon
from constants import NO_VARIANT, HEIGHT, WIDTH, TITLE
from maze import Maze
from room import Room
from tile import Tile, Chest
from pgzero.actor import Actor

game_ended = False

player = Actor("alien")
player.pos = WIDTH/2,HEIGHT - 120 - player.height/2
PLAYER_SPEED = 7.5
player.speed = 0

chest_icon = Actor("chest icon")
chest_icon.pos = (chest_icon.width,chest_icon.height)

mouse_hitbox = Rect((0,0),(2, 2))
go_left = False
go_right = False

mazes = []

symbols2 = {
"┼":(1,1,1,1),
"┴":(1,1,1,0),
"┬":(1,0,1,1),
"┤":(1,1,0,1),
"├":(0,1,1,1),
"┘":(1,1,0,0),
"└":(0,1,1,0),
"┐":(1,0,0,1),
"┌":(0,0,1,1),
"─":(1,0,1,0),
"│":(0,1,0,1),
"╸":(1,0,0,0),
"╹":(0,1,0,0),
"╺":(0,0,1,0),
"╻":(0,0,0,1),
}

def load_mazes():
    file = open("labirynty.txt", "r", encoding="utf-8")
    lines = file.readlines()
    x = 0
    while x < len(lines):
        width = int(lines[x])
        x += 1
        height = int(lines[x])
        rooms = []
        for i in range(height):
            x += 1
            line = lines[x]
            for j in range(width):
                rooms.append(Room(symbols2[line[j]],0,[]))
        mazes.append(Maze(width, height, rooms))
        x += 1

def set_up_game():
    global game_ended
    global maze
    global room_number
    global all_sprites
    global player_colliding
    global number_of_chests
    global number_of_found_chests

    game_ended = False

    maze_number = -1 #int(input("maze_number: "))
    if maze_number == -1:
        maze = Maze(randint(10,13),randint(4,6),[])
    else: 
        maze = mazes[maze_number]
    print(maze)

    player_colliding = []

    all_sprites = []
    room_number = 0
    number_of_chests = 0
    number_of_found_chests = 0

    make_tiles()

    build_room(room_number)

def iscolliding(object1,object2,distance):
    return (object1.right + distance > object2.left and 
            object1.left - distance < object2.right and 
            object1.top - distance < object2.bottom and 
            object1.bottom + distance > object2.top)

def make_tiles():
    for i in range(len(maze.rooms)):
        maze.rooms[i].set_distance(maze.distance[i])
        make_room_frame(i)
        make_addons(i)
        make_chests(i)
    add_more_chests()

def make_room_frame(i):
    brick = Actor("brick/0")
    ladder = Actor("ladder")
    for x in range(5):
        for y in range(3):
            maze.rooms[i].tiles.append(Tile("background",NO_VARIANT,(brick.width*(x + 3/2), brick.height*(y + 3/2))))
    y = 0
    for _ in range(2):
        x = 0
        for _ in range(2):
            for j in range(3):
                maze.rooms[i].tiles.append(Tile("brick",randint(0,7),(brick.width*(j + 1/2) + x, brick.height/2 + y)))
            x = WIDTH/2 + brick.width/2
        y = HEIGHT - brick.height
    if(maze.rooms[i].west() == 0):
        name, variant = "brick", randint(0,7)
    else:
        name, variant = "background", NO_VARIANT
    for j in range(3):
        maze.rooms[i].tiles.append(Tile(name,variant,(brick.width/2 , brick.height * (3/2 + j))))
    
    if(maze.rooms[i].north() == 0):
        maze.rooms[i].tiles.append(Tile("brick",randint(0,7),(WIDTH/2, brick.height/2)))
    else:
        maze.rooms[i].tiles.append(Tile("background",NO_VARIANT,(WIDTH/2, brick.height/2)))
        maze.rooms[i].tiles.append(Tile("ladder",NO_VARIANT,(WIDTH/2, ladder.height/2)))
    
    if(maze.rooms[i].east() == 0):
        name, variant = "brick", randint(0,7)
    else:
        name, variant = "background", NO_VARIANT
    for j in range(3):
        maze.rooms[i].tiles.append(Tile(name, variant,(WIDTH - brick.width/2, brick.height * (3/2 + j))))
    
    if(maze.rooms[i].south() == 0):
        maze.rooms[i].tiles.append(Tile("brick",randint(0,7),(WIDTH/2, HEIGHT - brick.height/2)))
    else:
        maze.rooms[i].tiles.append(Tile("background",NO_VARIANT,(WIDTH/2, HEIGHT - brick.height/2)))
        maze.rooms[i].tiles.append(Tile("ladder",NO_VARIANT,(WIDTH/2, HEIGHT)))

def make_addons(i):
    crack = Actor("crack")
    all_addons = [ #(name, number of variants, max number on screan, min distance, can_collide, x start, x end, y start, y end)
        Addon("torch",0,2,200,("background"),WIDTH/10, WIDTH*9/10, HEIGHT/2, HEIGHT/2),
        Addon("crack",0,3,100,("background"),crack.width/2, WIDTH - crack.width/2, HEIGHT/10, HEIGHT*7/8),
        Addon("crack",0,3,100,("brick"),crack.width/2, WIDTH - crack.width/2, HEIGHT/10, HEIGHT*7/8)
    ]
    if(i == 0):
        maze.rooms[i].tiles.append(Tile("door",NO_VARIANT,(WIDTH/2,HEIGHT - 120 - Actor("door").height/2)))
    for addon in all_addons:
        for _ in range(addon.max_number_on_screan):
            if(random() > 0.5):
                pos_avaible = False
                counter = 0
                if addon.number_of_variants == 0: 
                    variant = NO_VARIANT
                else:
                    variant = randint(0,addon.number_of_variants)
                while not (pos_avaible or counter > 20):
                    pos = (randint(addon.x_start,addon.x_end),randint(addon.y_start,addon.y_end))
                    pos_avaible = True
                    for tile in maze.rooms[i].tiles:
                        distance = 0
                        if(tile.name == addon.name):
                            distance = addon.min_distance
                        if(not tile.name in addon.can_collide and
                               iscolliding(Actor(addon.image(variant),pos),Actor(tile.image(),tile.pos),distance)): 
                            pos_avaible = False
                            break
                    counter += 1
                if pos_avaible:
                    maze.rooms[i].tiles.append(Tile(addon.name,variant,pos))

def make_chests(i):
    global number_of_chests
    if(maze.rooms[i].no_of_exits() == 1 and i != 0):
        chest_type = maze.rooms[i].chest_type()
        x = WIDTH*(randint(0,1)*2+1)/4
        if(maze.rooms[i].east() == 1):
            x = WIDTH/4
        elif(maze.rooms[i].west() == 1):
            x = WIDTH*3/4
        maze.rooms[i].tiles.append(Chest("chest",chest_type,x,False))
        number_of_chests += 1

def add_more_chests():
    global number_of_chests
    for i in range(len(maze.rooms)):
        for tile in maze.rooms[i].tiles:
            if isinstance(tile,Chest):
                maze.tiles_in_range(i,3)
                break
    print("")
    for i in range(len(maze.rooms)):
        max_allowed_distance = randrange(maze.size)
        if(maze.rooms[i].chest_is_allowed(max_allowed_distance)):
            chest_type = maze.rooms[i].chest_type()
            x = WIDTH*(randint(0,1)*2+1)/4
            if(maze.rooms[i].north() != 1 and maze.rooms[i].south() != 1):
                x = WIDTH/2
            if(chest_type > 0): chest_type -= 1
            maze.rooms[i].tiles.append(Chest("chest",chest_type,x,False))
            number_of_chests += 1
            maze.tiles_in_range(i,3)
    print(number_of_chests)

def build_room(i):
    global all_sprites
    all_sprites = []
    for tile in maze.rooms[i].tiles:
        tile_sprite = Actor(tile.image())
        tile_sprite.pos = tile.pos
        if isinstance(tile,Chest):
            tile_sprite.bottom = tile.bottom
        tile_sprite.name = tile.name
        all_sprites.append(tile_sprite)   

def player_colide():
    global player_colliding
    player_colliding = []
    for sprite in all_sprites:
        if(iscolliding(player,sprite,0)):
            player_colliding.append(sprite.name)

def player_move():
    global room_number
    global player_colliding
    player.x += player.speed
    player_colide()
    if "brick" in player_colliding:
        player.x -= player.speed
        player_colide()
    elif(player.x < player.width/2 and maze.rooms[room_number].west() == 1):
            room_number -= 1
            player.x = WIDTH - player.width/2
            build_room(room_number)
    elif(player.x > WIDTH - player.width/2 and maze.rooms[room_number].east() == 1):
            player.x = player.width/2
            room_number += 1
            build_room(room_number)

def animate_chests():
    chests = [tile for tile in maze.rooms[room_number].tiles if isinstance(tile,Chest)]
    for chest in chests:
        if chest.is_open and chest.frame < 6:
            chest.frame += 1
            build_room(room_number)

def exit_game():
    global game_ended
    print("game ended")
    game_ended = True

def on_key_down():
    global room_number
    if not game_ended:
        if keyboard.up:
            if("ladder" in player_colliding and maze.rooms[room_number].north() == 1):
                room_number -= maze.width
                build_room(room_number)
            elif("door" in player_colliding):
                exit_game()
        elif(keyboard.down and "ladder" in player_colliding and maze.rooms[room_number].south() == 1):
            room_number += maze.width
            build_room(room_number)
    elif keyboard.escape: set_up_game()

def on_mouse_up():
    global go_left
    global go_right
    go_left = False
    go_right = False

def on_mouse_down(pos):
    global go_left
    global go_right
    global mouse_hitbox
    global number_of_found_chests
    global room_number
    chests = [tile for tile in maze.rooms[room_number].tiles if isinstance(tile,Chest)]
    if(mouse.LEFT):
        mouse_hitbox.left = pos[0]-1
        mouse_hitbox.top = pos[1]-1
        if any(chests):
            for chest in chests:
                if(iscolliding(mouse_hitbox,Actor(chest.image(),chest.pos),10) and
                   not chest.is_open):
                    chest.is_open = True
                    number_of_found_chests += 1
        player_colide()
        if "ladder" in player_colliding:
            for sprite in all_sprites:
                if sprite.name == "ladder" and iscolliding(mouse_hitbox,sprite,10):
                    if(maze.rooms[room_number].north() == 1 and mouse_hitbox.bottom < HEIGHT/2):
                        room_number -= maze.width
                        build_room(room_number)
                    elif(maze.rooms[room_number].south() == 1 and mouse_hitbox.bottom > HEIGHT/2):
                        room_number += maze.width
                        build_room(room_number)    
        elif("door" in player_colliding):
            for sprite in all_sprites:
                if sprite.name == "door" and iscolliding(mouse_hitbox,sprite,10):
                    exit_game()
                    set_up_game()
        if pos[0] > WIDTH*3/4: go_right = True
        elif pos[0] < WIDTH/4: go_left = True

load_mazes()
set_up_game()

def draw():
    screen.clear()
    for sprite in all_sprites:
        sprite.draw()
    player.draw()
    chest_icon.draw()
    screen.draw.text(str(number_of_found_chests) + "/" + str(number_of_chests), center = chest_icon.pos, color="yellow", fontsize=50)

def update():
    if not game_ended:
        player.speed = 0
        if(keyboard.left or go_left):
            player.speed -= PLAYER_SPEED
        if(keyboard.right or go_right):
            player.speed += PLAYER_SPEED
        player_move()
        player_colide()
        animate_chests()   

async def main():
    pgzrun.go()
    await asyncio.sleep(0)

asyncio.run(main())
