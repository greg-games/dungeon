import pgzrun
import asyncio
import pygame
import numpy
import pygame.surfarray
import time

from pgzero.rect import Rect
from random import *
from addon import Addon
from constants import NO_VARIANT, HEIGHT, WIDTH, SCENE_WIDTH, UI_BAR_WIDTH, LEFT, RIGHT, TITLE, SOUND_NOT_PLAYING, SOUND_WILL_BE_PLAYED, SOUND_IS_PLAYING, NO_VARIABLE
from global_functions import iscolliding
from maze import Maze
from room import Room
from tile import Tile, AnimatedTile, Chest, Door
from entity import Entity, Player, Enemy, update_all_sprites
from loot import Loot
from pgzero.actor import Actor
from pgzero.loaders import sounds
from button import Button, all_buttons, buttons_in, buttons_out
from line import Line
from maze_map import MazeMap

seed(None)

game_ended = False

dt = 1
clock = pygame.time.Clock()

pygame.display.set_mode((WIDTH, HEIGHT))
player = Player()
player.pos = SCENE_WIDTH/2,HEIGHT - 120 - player.height/2 

loot_icons = []
hearts = []

chest_icon = Actor("ui/chest_icon")
ui_bar_left = Rect(0,0,UI_BAR_WIDTH,HEIGHT)
ui_bar_right = Rect(WIDTH - UI_BAR_WIDTH,0,UI_BAR_WIDTH,HEIGHT)

background = Actor("background",(WIDTH/2,HEIGHT/2))
map_background = Actor("map_background",(WIDTH/2,HEIGHT/2))

map_open = False
maze_map = None

mouse_hitbox = Rect((0,0),(2, 2))
go_left = False
go_right = False
go_up = False
go_down = False

all_loot = []

loot_collected = {
    "crystal_violet":0,
    "crystal_green":0,
    "crystal_red":0,
    "coin":0
}

show_hitboxes = False

mazes = []

TILE_FRAME_SPEED = 0.01

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

def make_ui():
    chest_icon.pos = (UI_BAR_WIDTH/2-chest_icon.width,2.3*chest_icon.height)
    pos =[(-2,1),(0,1),(2,1),(1,3)] #[(-2.5,1),(2,1),(-1.5,3),(1,3)]
    for (i, key) in enumerate(loot_collected.keys()):
        x,y = pos[i]
        loot_icon = Actor(f"ui/{key}_icon")
        loot_icon.pos = (UI_BAR_WIDTH/2 + loot_icon.width*x,loot_icon.height*y)
        loot_icon.name = key
        loot_icons.append(loot_icon)
    x = WIDTH - (UI_BAR_WIDTH*4/5) - 30
    for _ in range(5):
        heart = Actor(f"ui/heart")
        heart.lost = Actor(f"ui/lost_heart")
        heart.name = "heart"
        heart.pos = (x, heart.height * 1.5)
        heart.lost.pos = heart.pos
        x += UI_BAR_WIDTH/5
        hearts.append(heart)
    make_buttons()

def make_buttons():
    global duck_button, jump_button, attack_button, left_button, right_button, up_button, down_button, map_button
    map_button = Button("map",
                        on_click=(lambda a: toggle_map(), "NO_VARIABLE", "NO_VARIABLE"))
    map_button.set_pos((WIDTH-UI_BAR_WIDTH+map_button.width,HEIGHT-map_button.height))

    duck_button = Button("duck",
                         on_click=(lambda a: player.change_state("duck") 
                                   if player.state == "idle" or player.state == "running" 
                                   else None, "NO_VARIABLE", "NO_VARIABLE"))
    duck_button.set_pos((WIDTH-duck_button.width,HEIGHT/2+duck_button.height/2))

    jump_button = Button("jump",
                         on_click=(lambda a: player.change_state("jump")
                                   if player.state == "idle" or player.state == "running"
                                   else None, "NO_VARIABLE", "NO_VARIABLE"))
    jump_button.set_pos((WIDTH-jump_button.width,HEIGHT/2-jump_button.height/2))

    attack_button = Button("attack",
                           on_click=(lambda a: player.change_state("attack1")
                                     if player.state == "idle" or player.state == "running"
                                     else None, "NO_VARIABLE", "NO_VARIABLE"))
    attack_button.set_pos((WIDTH-attack_button.width*2,HEIGHT/2))
    
    move_button_center = (Actor("ui/buttons/left").width*3/2,HEIGHT - Actor("ui/buttons/left").height*3/2)

    left_button = Button("left",
                         on_click=(lambda a: True, "NO_VARIABLE", "go_left"),
                         on_release=(lambda a: False, "NO_VARIABLE", "go_left"))
    left_button.set_pos((move_button_center[0] - left_button.width,move_button_center[1]))

    right_button = Button("right",
                          on_click=(lambda a: True, "NO_VARIABLE", "go_right"),
                          on_release=(lambda a: False, "NO_VARIABLE", "go_right"))
    right_button.set_pos((move_button_center[0] + right_button.width,move_button_center[1]))

    up_button = Button("up",
                       on_click=(lambda a: (not go_down) and player.can_move, "NO_VARIABLE", "go_up"))
    up_button.set_pos((move_button_center[0],move_button_center[1]-up_button.height))

    down_button = Button("down",
                         on_click=(lambda a: (not go_up) and player.can_move, "NO_VARIABLE", "go_down"))
    down_button.set_pos((move_button_center[0],move_button_center[1]+down_button.height))

def buttons_on(event):
    for button in all_buttons:
        if event == "pressed":
            function = lambda input: button.on_press(input)
        elif event == "unpressed":
            function = lambda input: button.on_unpress(input)
        elif event == "clicked":
            function = lambda input: button.on_click(mouse_hitbox,input)
        elif event == "released":
            function = lambda input: button.on_release(input)
        
        if buttons_out[button.name][event] != None:
            x = function(globals()[buttons_in[button.name][event]])
            if x != None:
                globals()[buttons_out[button.name][event]] = x
        else:
            function(None)

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
    global maze_map
    global room_number
    global all_sprites
    global all_loot
    global number_of_chests
    global number_of_found_chests
    global no_visited_rooms

    maze_number = -1 #int(input("maze_number: "))
    if maze_number == -1:
        maze = Maze(randint(10,13),randint(4,6),[])
    else: 
        maze = mazes[maze_number]
    print(maze)

    maze_map = MazeMap(maze)

    player.change_x(SCENE_WIDTH/2)
    player.change_state("idle")
    player.is_dead = False

    player.colliding = []

    attack_button.disable()

    all_sprites = []
    all_loot = []

    room_number = 0
    toggle_map(set_to = False)
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
    brick = Actor("tiles/brick/variant_0")

    def make_wall(exit, x):
        if(exit == 0):
            for j in range(HEIGHT//brick.height - 2):
                maze.rooms[i].tiles_add(Tile("brick", randint(0,7),(x, brick.height * (3/2 + j))))
    
    def make_ladder(exit, y1, y2):
        if(exit == 0):
            maze.rooms[i].tiles_add(Tile("brick",randint(0,7),(SCENE_WIDTH/2, y1)))
        else:
            maze.rooms[i].tiles_add(Tile("ladder",NO_VARIANT,(SCENE_WIDTH/2, y2)))

    y = 0
    for _ in range(2):
        x = 0
        for _ in range(2):
            for j in range((SCENE_WIDTH - 1)//(2*brick.width)):
                maze.rooms[i].tiles_add(Tile("brick",randint(0,7),(brick.width*(j + 1/2) + x, brick.height/2 + y)))
            x = SCENE_WIDTH/2 + brick.width/2
        y = HEIGHT - brick.height

    make_wall(maze.rooms[i].west(), brick.width/2)
    make_ladder(maze.rooms[i].north(), brick.height/2, (HEIGHT-brick.height)/2)
    make_wall(maze.rooms[i].east(), SCENE_WIDTH - brick.width/2)
    make_ladder(maze.rooms[i].south(), HEIGHT - brick.height/2, HEIGHT)

def make_addons(i):
    crack = Actor("tiles/crack/variant_0")
    all_addons = [ #(name, number of variants, max number on screan, min distance, x start, x end, y start, y end)
        Addon("candle",1,2,200,SCENE_WIDTH/10, SCENE_WIDTH*9/10, HEIGHT/2, HEIGHT/2),
        Addon("crack",10,3,100,crack.width/2, SCENE_WIDTH - crack.width/2, HEIGHT/10, HEIGHT/2),
    ]
    if(i == 0):
        maze.rooms[i].tiles_add(Door("door",0,"closing",(SCENE_WIDTH/2,HEIGHT - 120 - Actor("tiles/door/variant_0/closing/0").height/2)))
        maze.rooms[i].animated_tiles_indexes.append(len(maze.rooms[i].tiles) - 1)
        maze.rooms[i].tiles[-1].is_animating = True
    for addon in all_addons:
        for _ in range(addon.max_number_on_screan):
            if(random() > 0.5):
                if addon.number_of_variants == 0: 
                    variant = NO_VARIANT
                else:
                    variant = randint(0,addon.number_of_variants)
                new_addon = Tile(addon.name,variant)
                counter = 0
                while(counter < 20):
                    new_addon.pos = (randint(addon.x_start,addon.x_end),randint(addon.y_start,addon.y_end))
                    pos_avaible = True
                    for tile in maze.rooms[i].tiles:
                        distance = 0
                        if(tile.name == addon.name):
                            distance = addon.min_distance
                        if(iscolliding(Actor(new_addon.image(),new_addon.pos),Actor(tile.image(),tile.pos),distance)):
                            pos_avaible = False
                            break
                    counter += 1
                    if pos_avaible:
                        maze.rooms[i].tiles_add(new_addon)
                        break

def make_chests(i):
    global number_of_chests
    if(maze.rooms[i].no_of_exits() == 1 and i != 0):
        chest_type = maze.rooms[i].chest_type()
        x = SCENE_WIDTH*(randint(0,1)*2+1)/4
        if(maze.rooms[i].east() == 1):
            x = SCENE_WIDTH/4
        elif(maze.rooms[i].west() == 1):
            x = SCENE_WIDTH*3/4
        maze.rooms[i].tiles_add(Chest("chest",chest_type,x))
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
            x = SCENE_WIDTH*(randint(0,1)*2+1)/4
            if(maze.rooms[i].north() != 1 and maze.rooms[i].south() != 1):
                x = SCENE_WIDTH/2
            if(chest_type > 0): chest_type -= 1
            maze.rooms[i].tiles_add(Chest("chest",chest_type,x))
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
    update_all_sprites(all_sprites)
    for room in maze.rooms:
        room.last_visited += 1
    maze.rooms[i].last_visited = 0
    maze.rooms[i].visited = True

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
    if room.has_closed_chest and room.no_skeletons == 0:
        room.no_skeletons += 1
        spawn_skeleton()
    elif (room.skeleton_is_allowed() and 
          random() < skeleton_chance(no_visited_rooms/maze.size)) :
        if (random() < 0.5 and not ("ladder" in room.tiles_names)):
            room.no_skeletons += 1
            spawn_skeleton()
        room.no_skeletons += 1
        spawn_skeleton()

def spawn_skeleton():
    skeleton = Enemy("skeleton","variant_0")
    skeleton.y = HEIGHT - 120 - skeleton.height/2
    for _ in range(1000):
        x = SCENE_WIDTH/2 + (SCENE_WIDTH/4-30)*(2*randint(0,1)-1)+randint(-(SCENE_WIDTH)/4+150,(SCENE_WIDTH)/4-150)
        skeleton.change_x(x)
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
    return min(2**(2*(x-3)) + 0.075, 0.75)

def update_buttons():
    buttons_on("unpressed")
    buttons_on("pressed")
    for thing in player.attacking:
        if (thing.name == "skeleton" and thing.state == "idle" and
            player.state != "hit" and  player.state != "die"):
            attack_button.enable()
            break
        else:
            attack_button.disable()

def change_player_speed():
    player.speed = 0
    if(((keyboard.left or keyboard.a  or go_left) ^ (keyboard.right or keyboard.d or go_right)) and player.can_move):
        player.speed = player.running_speed*dt
        if player.state == "running" or player.state == "idle":
            if(keyboard.left or keyboard.a or go_left):
                if player.dir == RIGHT:
                    player.x -= player.width/20
                player.dir = LEFT
            else:
                if player.dir == LEFT:
                    player.x += player.width/20
                player.dir = RIGHT           

def pressing_up_or_down():
    global room_number, go_down, go_up
    if not game_ended:
        if go_up:
            for thing in player.colliding:
                if(thing.name == "ladder" and maze.rooms[room_number].north() == 1):
                    sounds.ladder.ladder.play()
                    room_number -= maze.width
                    build_room(room_number)
                    break
                elif(thing.name =="door"):
                    exit_game()
                    break
        elif(go_down and maze.rooms[room_number].south() == 1):
            for thing in player.colliding:
                if thing.name == "ladder":
                    sounds.ladder.ladder.play()
                    room_number += maze.width
                    build_room(room_number)
                    break
        go_up,go_down = False, False

def realign_player():
    global room_number
    player.update_colliding()
    for thing in player.colliding:
        if ((thing.name == "brick" or thing.name == "skeleton") and player.islookingat(thing)):
            player.change_x(player.x - player.speed*player.dir)
            if (player.state == "running"):
                player.change_state("idle")
            player.update_colliding()
            break
    if(player.x < player.hitbox.width*0.6 and maze.rooms[room_number].west() == 1):
        room_number -= 1
        player.change_x(SCENE_WIDTH - player.hitbox.width*0.61)
        build_room(room_number)
    elif(player.x > SCENE_WIDTH - player.hitbox.width*0.6 and maze.rooms[room_number].east() == 1):
        room_number += 1
        player.change_x(player.hitbox.width*0.61)
        build_room(room_number)

def entity_move():
    for sprite in all_sprites:
        if isinstance(sprite,Enemy):
            if sprite.is_dead:
                maze.rooms[room_number].enemies.remove(sprite)
                all_sprites.remove(sprite)
                maze.rooms[room_number].no_skeletons -= 1
                if maze.rooms[room_number].has_closed_chest:
                    open_chest(maze.rooms[room_number].tiles[maze.rooms[room_number].animated_tiles_indexes[0]])
            else:
                if (sprite.state == "running" or sprite.frame == 0):
                    if sprite.x > player.x:
                        sprite.dir = LEFT
                    else:
                        sprite.dir = RIGHT
                    sprite.update_colliding()
                    can_move = True
                    for thing in sprite.colliding:
                        if (thing.name == "player" or (thing.name == "skeleton" and sprite.islookingat(thing))):
                            can_move = False
                    if can_move:
                        sprite.go_to_player(player.x,dt)
                        sprite.move()
                sprite.update_colliding()
                for thing in sprite.colliding:
                    if thing.name == "skeleton" and sprite.islookingat(thing):
                        sprite.x -= sprite.speed*sprite.dir
                        sprite.change_state("idle")
                        sprite.speed = 0
                        sprite.update_colliding()
                    if (thing.name == "player"):
                        sprite.x -= sprite.speed*sprite.dir
                        if thing.state == "hit":
                            sprite.attack_progress = 1
                        sprite.attack()
    player.move()
    realign_player()

def animate_loot():
    if len(all_loot) > 0:
        player.can_move = False
        if all_loot[-1].is_animating_finished(dt):
            loot_collected[all_loot[-1].name] += 1
            all_sprites.remove(all_loot.pop())
    else:
        player.can_move = not map_open

def animate_entities():
    player.animate(dt)
    for sprite in all_sprites:
        if isinstance(sprite,Enemy):
            sprite.animate(dt)
            
def animate_tiles():
    for i in range(len(maze.rooms[room_number].tiles)):
        tile = maze.rooms[room_number].tiles[i]
        if isinstance(tile,AnimatedTile):
            tile.next_frame(TILE_FRAME_SPEED*dt)
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

def open_chest(chest):
    global number_of_found_chests
    chest.is_animating = True
    number_of_found_chests += 1
    maze.rooms[room_number].has_closed_chest = False
    sounds.load(chest.sound_path()).play()
    for type in chest.loot_table.keys():
        for _ in range(randint(chest.loot_table[type][0],chest.loot_table[type][1])):
            loot = Loot(type,chest.pos)
            all_sprites.append(loot)
            all_loot.append(loot)   

def toggle_map(set_to:bool = None):
    global map_open
    if set_to != None:
        map_open = set_to
    else:
        map_open = not map_open
    if map_open:
        player.can_move = False
        jump_button.disable()
        duck_button.disable()
    else:
        player.can_move = len(all_loot) == 0
        jump_button.enable()
        duck_button.enable() 

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

def on_death():
    player.health = 5
    for key in loot_collected.keys():
        loot_collected[key] = 0

def on_key_down():
    global go_down, go_up
    if player.can_move:
        if keyboard.up or keyboard.w:
            go_up = True
        elif keyboard.down or keyboard.s:
            go_down = True
    if player.state == "idle":
        if keyboard.lshift and jump_button.can_interact:
            player.change_state("jump")
        elif keyboard.lctrl and duck_button.can_interact:
            player.change_state("duck")
        elif keyboard.space and attack_button.can_interact:
            player.change_state("attack1")

def on_mouse_up():
    buttons_on("released")

def on_mouse_down(pos):
    if(mouse.LEFT):
        buttons_on("clicked")

def on_mouse_move(pos):
    mouse_hitbox.left = pos[0]-1
    mouse_hitbox.top = pos[1]-1

def draw_sceen():
    background.draw()
    for sprite in all_sprites:
        sprite.x += UI_BAR_WIDTH
        sprite.draw()
        sprite.x -= UI_BAR_WIDTH
        if isinstance(sprite,Entity) and show_hitboxes:
            sprite.hitbox.x += UI_BAR_WIDTH
            sprite.attack_hitbox.x += UI_BAR_WIDTH
            screen.draw.rect(sprite.hitbox,"green",3)
            screen.draw.rect(sprite.attack_hitbox,"red",3)
            sprite.hitbox.x -= UI_BAR_WIDTH
            sprite.attack_hitbox.x -= UI_BAR_WIDTH
    player.x += UI_BAR_WIDTH
    player.draw()
    player.x -= UI_BAR_WIDTH

def draw_ui():
    pygame.draw.rect(screen.surface, (58,58,58), ui_bar_left)
    pygame.draw.rect(screen.surface, (58,58,58), ui_bar_right)
    chest_icon.draw()
    for i in range(len(hearts)):
        if player.health > i:
            hearts[i].draw()
        else:
            hearts[i].lost.draw()
    for button in all_buttons:
            button.background.draw()
            button.draw()
    for thing in loot_icons:
        thing.draw()
        screen.draw.text(str(loot_collected[thing.name]), midleft = (thing.pos[0] + thing.width/2, thing.pos[1]), color="white", fontsize=50)
    screen.draw.text(str(number_of_found_chests) + "/" + str(number_of_chests), center = chest_icon.pos, color="yellow", fontsize=50)

load_mazes()
make_ui()
set_up_game()

#show_hitboxes = True # for debugging only
def draw():
    screen.clear()
    draw_sceen()
    draw_ui()
    if map_open:
        map_background.draw()
        maze_map.draw(maze)

def update():
    global game_ended, dt
    dt = clock.tick(60)
    if not game_ended:
        pressing_up_or_down()
        change_player_speed()
        entity_move()
        update_buttons()
        animate_tiles()
        animate_entities()
        animate_loot()
        play_sounds()
        if player.is_dead:
            game_ended = True
            on_death()
            set_up_game()

async def main():
    pgzrun.go()
    await asyncio.sleep(0)

asyncio.run(main())