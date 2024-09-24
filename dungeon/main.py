import sys
import pgzrun
import asyncio

from random import *
from addon import Addon
from constants import NO_VARIANT, HEIGHT, WIDTH, TITLE,SOUND_NOT_PLAYING, SOUND_WILL_BE_PLAYED, SOUND_IS_PLAYING
from global_functions import iscolliding
from maze import Maze
from room import Room
from tile import Tile, AnimatedTile, Chest, Door
from entity import Player, Enemy, all_entities
from pgzero.actor import Actor
from pgzero.loaders import sounds

seed(None)

game_ended = False

player = Player()
player.pos = WIDTH/2,HEIGHT - 120 - player.height/2

chest_icon = Actor("chest icon/variant_0")
chest_icon.pos = (chest_icon.width,chest_icon.height)

mouse_hitbox = Rect((0,0),(2, 2))
go_left = False
go_right = False

mazes = []

TILE_FRAME_SPEED = 0.5
ENTITY_FRAME_SPEED = 0.2

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

def is_in_browser():
    return sys.platform == "emscripten"
    #return True #for debug purposes

if is_in_browser():
    player.running_speed *= 1.75
    TILE_FRAME_SPEED = 1
    ENTITY_FRAME_SPEED = 0.5

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
    global number_of_chests
    global number_of_found_chests
    global no_visited_rooms

    maze_number = -1 #int(input("maze_number: "))
    if maze_number == -1:
        maze = Maze(randint(10,13),randint(4,6),[])
    else: 
        maze = mazes[maze_number]
    print(maze)

    player.change_x(WIDTH/2)

    player.colliding = []

    all_sprites = []
    room_number = 0
    number_of_chests = 0
    number_of_found_chests = 0
    no_visited_rooms = 0

    make_tiles()

    build_room(room_number)

    game_ended = False

def make_tiles():
    for i in range(len(maze.rooms)):
        maze.rooms[i].set_distance(maze.distance[i])
        make_room_frame(i)
        make_addons(i)
        make_chests(i)
    add_more_chests()

def make_room_frame(i):
    brick = Actor("brick/variant_0")
    ladder = Actor("ladder/variant_0")
    for x in range(WIDTH//brick.width - 2):
        for y in range(HEIGHT//brick.height - 2):
            maze.rooms[i].tiles.append(Tile("background",NO_VARIANT,(brick.width*(x + 3/2), brick.height*(y + 3/2))))
    y = 0
    for _ in range(2):
        x = 0
        for _ in range(2):
            for j in range((WIDTH - 1)//(2*brick.width)):
                maze.rooms[i].tiles.append(Tile("brick",randint(0,7),(brick.width*(j + 1/2) + x, brick.height/2 + y)))
            x = WIDTH/2 + brick.width/2
        y = HEIGHT - brick.height
    if(maze.rooms[i].west() == 0):
        name, variant = "brick", randint(0,7)
    else:
        name, variant = "background", NO_VARIANT
    for j in range(HEIGHT//brick.height - 2):
        maze.rooms[i].tiles.append(Tile(name,variant,(brick.width/2 , brick.height * (3/2 + j))))
    
    if(maze.rooms[i].north() == 0):
        maze.rooms[i].tiles.append(Tile("brick",randint(0,7),(WIDTH/2, brick.height/2)))
    else:
        maze.rooms[i].tiles.append(Tile("background",NO_VARIANT,(WIDTH/2, brick.height/2)))
        maze.rooms[i].tiles.append(Tile("ladder",NO_VARIANT,(WIDTH/2, ladder.height/2)))
        maze.rooms[i].north_ladder_index = len(maze.rooms[i].tiles) - 1
    
    if(maze.rooms[i].east() == 0):
        name, variant = "brick", randint(0,7)
    else:
        name, variant = "background", NO_VARIANT
    for j in range(HEIGHT//brick.height - 2):
        maze.rooms[i].tiles.append(Tile(name, variant,(WIDTH - brick.width/2, brick.height * (3/2 + j))))
    
    if(maze.rooms[i].south() == 0):
        maze.rooms[i].tiles.append(Tile("brick",randint(0,7),(WIDTH/2, HEIGHT - brick.height/2)))
    else:
        maze.rooms[i].tiles.append(Tile("background",NO_VARIANT,(WIDTH/2, HEIGHT - brick.height/2)))
        maze.rooms[i].tiles.append(Tile("ladder",NO_VARIANT,(WIDTH/2, HEIGHT)))
        maze.rooms[i].south_ladder_index = len(maze.rooms[i].tiles) - 1

def make_addons(i):
    crack = Actor("crack/variant_0")
    all_addons = [ #(name, number of variants, max number on screan, min distance, can_collide, x start, x end, y start, y end)
        Addon("torch",0,2,200,("background"),WIDTH/10, WIDTH*9/10, HEIGHT/2, HEIGHT/2),
        Addon("crack",0,3,100,("background"),crack.width/2, WIDTH - crack.width/2, HEIGHT/10, HEIGHT*7/8),
        Addon("crack",0,3,100,("brick"),crack.width/2, WIDTH - crack.width/2, HEIGHT/10, HEIGHT*7/8)
    ]
    if(i == 0):
        maze.rooms[i].tiles.append(Door("door",0,"closing",(WIDTH/2,HEIGHT - 120 - Actor("door/variant_0/closing/0").height/2)))
        maze.rooms[i].animated_tiles_indexes.append(len(maze.rooms[i].tiles) - 1)
        maze.rooms[i].tiles[-1].is_animating = True
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
        maze.rooms[i].tiles.append(Chest("chest",chest_type,x))
        maze.rooms[i].animated_tiles_indexes.append(len(maze.rooms[i].tiles) - 1)
        maze.rooms[i].has_closed_chest = True

        number_of_chests += 1

def add_more_chests():
    global number_of_chests
    for i in range(len(maze.rooms)):
        for tile in maze.rooms[i].tiles:
            if isinstance(tile,Chest):
                for room in maze.rooms_in_range(i,3):
                    room.is_chest_in_range = True
                break
    for i in range(len(maze.rooms)):
        max_allowed_distance = randrange(maze.size)
        if(maze.rooms[i].chest_is_allowed(max_allowed_distance)):
            chest_type = maze.rooms[i].chest_type()
            x = WIDTH*(randint(0,1)*2+1)/4
            if(maze.rooms[i].north() != 1 and maze.rooms[i].south() != 1):
                x = WIDTH/2
            if(chest_type > 0): chest_type -= 1
            maze.rooms[i].tiles.append(Chest("chest",chest_type,x))
            maze.rooms[i].animated_tiles_indexes.append(len(maze.rooms[i].tiles) - 1)
            maze.rooms[i].has_closed_chest = True
            number_of_chests += 1
            for room in maze.rooms_in_range(i,3):
                room.is_chest_in_range = True

def build_room(i):
    global all_sprites
    global no_visited_rooms
    no_visited_rooms += 1
    add_skeletons()
    all_sprites = []
    for tile in maze.rooms[i].tiles:
        tile_sprite = Actor(tile.image())
        tile_sprite.pos = tile.pos
        if isinstance(tile,Chest):
            tile_sprite.bottom = tile.bottom
        tile_sprite.name = tile.name
        all_sprites.append(tile_sprite)
    for enemy in maze.rooms[i].enemies:
        all_sprites.append(enemy)
    all_sprites.append(player)
    for room in maze.rooms:
        room.last_visited += 1
    maze.rooms[i].last_visited = 0

def maze_printable(func):
    def wrapper():
        print("")
        func()
        for i, room in enumerate(maze.rooms):
            if(i%maze.width == 0):
                print("")
            print(maze.rooms[i], end= "")
            if i == room_number:
                print("*",end= "  ")
            elif maze.rooms[i].no_skeletons == 1:
                print("s",end= "  ")
            elif maze.rooms[i].no_skeletons == 2:
                print("ss",end= " ")
            elif maze.rooms[i].skeleton_is_allowed():
                print(1,end= "  ")
            else:
                print(0,end= "  ")
        print(str(no_visited_rooms) + " / " + str(maze.size),end= " ")
        print(str(round(skeleton_chance(no_visited_rooms/maze.size)*100)) + "%")
    return wrapper

@maze_printable
def add_skeletons():
    room = maze.rooms[room_number]
    if room.skeleton_is_allowed():
        if room.has_closed_chest:
            room.no_skeletons += 1
            spawn_skeleton()
        else:
            if (random() < skeleton_chance(no_visited_rooms/maze.size)):
                if (random() < 0.5):
                    room.no_skeletons += 1
                    spawn_skeleton()
                room.no_skeletons += 1
                spawn_skeleton()
    # start of symulating fight
    #if room.no_skeletons > 0:
        #room.no_skeletons -= 1
    # end of symulating fight

def spawn_skeleton():
    skeleton = Enemy("skeleton","variant_0")
    skeleton.y = HEIGHT - 120 - skeleton.height/2
    for _ in range(1000):
        x = WIDTH/2 + (WIDTH/4-30)*(2*randint(0,1)-1)+randint(-(WIDTH)/4+150,(WIDTH)/4-150)
        skeleton.x = x
        can_spawn = True
        for enemy in maze.rooms[room_number].enemies:
            if iscolliding(skeleton,enemy,10):
                can_spawn = False
                break
        if can_spawn:
            break
    if can_spawn:
        maze.rooms[room_number].enemies.append(skeleton)

def skeleton_chance(x):
    return min(100*(2 ** (2*x -12)) + 0.22, 0.75)

def change_player_speed():
    player.speed = 0
    if(keyboard.left or go_left):
        player.speed -= player.running_speed
    if(keyboard.right or go_right):
        player.speed += player.running_speed

def realign_player():
    global room_number
    player.update_colliding(all_sprites)
    if ("brick" in player.colliding or "skeleton" in player.colliding):
        player.x -= player.speed
        player.change_state("idle")
        player.update_colliding(all_sprites)
    if(player.x < player.hitbox.width/2 and maze.rooms[room_number].west() == 1):
        room_number -= 1
        player.change_x(WIDTH - player.hitbox.width/2)
        build_room(room_number)
    elif(player.x > WIDTH - player.hitbox.width/2 and maze.rooms[room_number].east() == 1):
        room_number += 1
        player.change_x(player.hitbox.width/2)
        build_room(room_number)

def entity_move():
    for sprite in all_sprites:
        if isinstance(sprite,Enemy):
            if sprite.x > player.x:
                sprite.dir = "left"
            else:
                sprite.dir = "right"
            sprite.update_colliding(all_sprites)
            if not ("player" in sprite.colliding or "skeleton" in sprite.colliding):
                sprite.go_to_player(player.x)
                sprite.move()
            sprite.update_colliding(all_sprites)
            if ("player" in sprite.colliding or "skeleton" in sprite.colliding):
                sprite.x -= sprite.speed
                if (sprite.state == "running" or sprite.frame == 0):
                    if ((not "player" in sprite.colliding) or (sprite.state != "idle" and random() < 0.5)):
                        sprite.change_state("idle")
                    elif random() < 0.5:
                        sprite.change_state("attack1")
                    else:
                        sprite.change_state("attack2")
                sprite.speed = 0
                sprite.update_colliding(all_sprites)
    player.move()

def animate_entities():
    for entity in all_entities:
        entity.animate(ENTITY_FRAME_SPEED)

def animate_tiles():
    for i in range(len(maze.rooms[room_number].tiles)):
        tile = maze.rooms[room_number].tiles[i]
        if isinstance(tile,AnimatedTile):
            tile.next_frame(TILE_FRAME_SPEED)
            all_sprites[i].image = tile.image()
            if isinstance(tile,Chest):
                all_sprites[i].bottom = tile.bottom
            if(tile.name == "door" and tile.has_finished_animating):
                tile.is_animating = False
                tile.frame = 0
                if tile.state == "closing":
                    sounds.load(tile.sound_path()).play()
                    tile.state = "opening"
                    tile.has_finished_animating = False
                else:
                    exit_game()
                    break

def play_sounds():
    for sound in player.all_sounds:
        if player.all_sounds[sound] == SOUND_WILL_BE_PLAYED:
            player.all_sounds[sound] = SOUND_IS_PLAYING
            sounds.load(player.sound_path(sound)).play(-1)
        elif player.all_sounds[sound] == SOUND_NOT_PLAYING:
            sounds.load(player.sound_path(sound)).stop()

def exit_game():
    global game_ended
    print("game ended")
    game_ended = True
    set_up_game()

def on_key_down():
    global room_number
    if not game_ended:
        if keyboard.up:
            if("ladder" in player.colliding and maze.rooms[room_number].north() == 1):
                room_number -= maze.width
                build_room(room_number)
            elif("door" in player.colliding):
                exit_game()
        elif(keyboard.down and "ladder" in player.colliding and maze.rooms[room_number].south() == 1):
            room_number += maze.width
            build_room(room_number)

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
    if(mouse.LEFT):
        mouse_hitbox.left = pos[0]-1
        mouse_hitbox.top = pos[1]-1
        clicked_on_anything = False
        for i in range(len(maze.rooms[room_number].animated_tiles_indexes)):
            tile_sprite = all_sprites[maze.rooms[room_number].animated_tiles_indexes[i]]
            tile = maze.rooms[room_number].animated_tile(i)
            if(tile.triger == "click" and iscolliding(mouse_hitbox,tile_sprite,10)):
                clicked_on_anything = True
                if not tile.is_animating:
                    if tile.name == "door":
                        if (tile.variant == 0 and "door" in player.colliding):
                            tile.is_animating = True
                            sounds.load(tile.sound_path()).play()
                    else:
                        tile.is_animating = True
                        if tile.name == "chest":
                            number_of_found_chests += 1
                            maze.rooms[room_number].has_closed_chest = False
                            sounds.load(tile.sound_path()).play()
        if(maze.rooms[room_number].north_ladder_index > -1 
           and "ladder" in player.colliding):
            ladder = all_sprites[maze.rooms[room_number].north_ladder_index]
            if (iscolliding(mouse_hitbox,ladder,10) 
                and mouse_hitbox.bottom < HEIGHT/2):
                sounds.ladder.ladder.play()
                room_number -= maze.width
                build_room(room_number)
        if(maze.rooms[room_number].south_ladder_index > -1 
           and "ladder" in player.colliding):
            ladder = all_sprites[maze.rooms[room_number].south_ladder_index]
            if (iscolliding(mouse_hitbox,ladder,10) and mouse_hitbox.bottom > HEIGHT/2):
                sounds.ladder.ladder.play()
                room_number += maze.width
                build_room(room_number) 
        if not clicked_on_anything:
            if pos[0] > WIDTH*5/8: go_right = True
            elif pos[0] < WIDTH*3/8: go_left = True

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
        change_player_speed()
        entity_move()
        realign_player()
        animate_tiles()
        animate_entities()  
        play_sounds()

async def main():
    pgzrun.go()
    await asyncio.sleep(0)

asyncio.run(main())
