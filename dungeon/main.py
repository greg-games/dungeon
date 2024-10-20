import pygame
import pgzrun
import pygame.surfarray
import asyncio
import numpy
import time

from pgzero.actor import Actor
from pgzero.rect import Rect
from pgzero.loaders import sounds
from random import *
from constants import *
from global_functions import iscolliding
pygame.display.set_mode((WIDTH, HEIGHT))
from maze import Maze
from room import Room
from tile import Tile, TileAddon, AnimatedTile, Chest, Door
from addon import Addon, all_addons
from entity import Entity, Player, Enemy, update_all_sprites
from loot import Loot
from button import Button, all_buttons, buttons_in, buttons_out
from maze_map import MazeMap

seed(None)

game_ended = True

dt = 1
clock = pygame.time.Clock()

player = Player()
player.pos = SCENE_WIDTH/2,HEIGHT - 120 - player.height/2 

loot_icons = []
hearts = []

chest_icon = Actor("ui/chest_icon")
ui_bar_left = Rect(0,0,UI_BAR_WIDTH,HEIGHT)
ui_bar_right = Rect(WIDTH - UI_BAR_WIDTH,0,UI_BAR_WIDTH,HEIGHT)

background = Actor("background/game",(WIDTH/2,HEIGHT/2))

map_open = False
maze_map = None

mouse_hitbox = Rect((0,0),(2, 2))
go_left = False
go_right = False
go_up = False
go_down = False

floor = 0

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
    pos =[(-2,1),(0,1),(2,1),(1,3)]
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
    global duck_button, jump_button, attack_button, left_button, right_button, up_button, down_button, map_button, play_button

    play_button = Button("play",
                        on_release=(lambda a: set_up_game(), "NO_VARIABLE", "NO_VARIABLE"))
    play_button.set_pos((WIDTH/2,HEIGHT*3/4))

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
            function = lambda input: button.on_release(mouse_hitbox,input)
        
        if buttons_out[button.name][event] != None:
            x = function(globals()[buttons_in[button.name][event]])
            if x != None:
                globals()[buttons_out[button.name][event]] = x
        else:
            function(None)

def current_room():
    return maze.rooms[room_number]

def load_mazes():
    file = open("labirynty.txt", "r", encoding="utf-8")
    lines = file.readlines()
    x = 0
    while x < len(lines):
        width = int(lines[x])
        x += 1
        height = int(lines[x])
        rooms = []
        for _ in range(height):
            x += 1
            line = lines[x]
            for i in range(width):
                rooms.append(Room(symbols2[line[i]],0,[]))
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
    global floor

    floor += 1

    maze_number = -1 #int(input("maze_number: "))
    if maze_number == -1:
        maze = Maze(min(randint(floor+4,floor+5),13),min(randint(floor//2+2,floor//2+3),8),[])
    else: 
        maze = mazes[maze_number]
    print(maze)

    maze_map = MazeMap(maze)

    player.change_x(SCENE_WIDTH/2)
    player.change_state("idle")
    player.is_dead = False

    player.colliding = []

    background.image = "background/game"

    for button in all_buttons:
        button.show()
    play_button.hide()
    attack_button.disable()

    all_sprites = []
    all_loot = []

    room_number = 0
    toggle_map(set_to = False)
    number_of_chests = 0
    number_of_found_chests = 0
    no_visited_rooms = 0

    make_tiles()

    build_room()

    game_ended = False

def make_tiles():
    for i, room in enumerate(maze.rooms):
        room.set_distance(maze.distance[i])
        make_room_frame(room)
        if (i == 0):
            make_door()
        elif room.is_dead_end():
            make_chests(room)
    add_more_chests()
    for room in maze.rooms:
        make_addons(room)

def make_room_frame(room):
    brick = Actor("tiles/brick/variant_0")

    def make_wall(exit, x):
        if not exit:
            for j in range(HEIGHT//brick.height - 2):
                room.tiles_add(Tile("brick", randint(0,7),(x, brick.height * (3/2 + j))))
    
    def make_ladder(exit, y_brick, y_ladder):
        if not exit:
            room.tiles_add(Tile("brick",randint(0,7),(SCENE_WIDTH/2, y_brick)))
        else:
            room.tiles_add(Tile("ladder",NO_VARIANT,(SCENE_WIDTH/2, y_ladder)))

    y = 0
    for _ in range(2):
        x = 0
        for _ in range(2):
            for j in range((SCENE_WIDTH - 1)//(2*brick.width)):
                room.tiles_add(Tile("brick",randint(0,7),(brick.width*(j + 1/2) + x, brick.height/2 + y)))
            x = SCENE_WIDTH/2 + brick.width/2
        y = HEIGHT - brick.height

    make_wall(room.west(), brick.width/2)
    make_ladder(room.north(), brick.height/2, (HEIGHT-brick.height)/2)
    make_wall(room.east(), SCENE_WIDTH - brick.width/2)
    make_ladder(room.south(), HEIGHT - brick.height/2, HEIGHT)

def make_addons(room):
    for addon in all_addons:
        for _ in range(addon.max_number_on_screan):
            if(random() < addon.chance):
                variant = randrange(addon.number_of_variants)
                new_addon = TileAddon(addon.name,variant)
                for _ in range(20):
                    new_addon.pos = (randint(addon.x_start,addon.x_end),randint(addon.y_start,addon.y_end))
                    pos_avaible = True
                    for tile in room.tiles:
                        if (not hasattr(addon,"can_collide") or tile.name != addon.can_collide):
                            distance = 0
                            if(tile.name == addon.name):
                                distance = addon.min_distance
                            if(iscolliding(Actor(new_addon.image(),new_addon.pos),Actor(tile.image(),tile.pos),distance)):
                                pos_avaible = False
                                break
                    if pos_avaible:
                        room.tiles_add(new_addon)
                        break

def make_chests(room):
    global number_of_chests
    room.add_chest(floor)
    number_of_chests += 1

def add_more_chests():
    global number_of_chests
    for i, room in enumerate(maze.rooms):
        for tile in room.tiles:
            if isinstance(tile,Chest):
                for room_in_range in maze.rooms_in_range(i,3):
                    room_in_range.is_chest_in_range = True
                break
    for i,room in enumerate(maze.rooms):
        max_allowed_distance = randrange(maze.size)
        if(room.chest_is_allowed(max_allowed_distance)):        
            room.add_chest(floor)
            number_of_chests += 1
            for room_in_range in maze.rooms_in_range(i,3):
                room_in_range.is_chest_in_range = True

def make_door():
    room = maze.rooms[0]
    room.tiles_add(Door("door",0,"closing",(SCENE_WIDTH/2,HEIGHT - 120 - Actor("tiles/door/variant_0/closing/0").height/2)))
    room.tiles[-1].is_animating = True

def build_room():
    global all_sprites
    global no_visited_rooms
    room = current_room()
    no_visited_rooms += 1
    add_skeletons()
    all_sprites = []
    for tile in room.tiles:
        tile_sprite = Actor(tile.image())
        tile_sprite.pos = tile.pos
        if isinstance(tile,Chest):
            tile_sprite.bottom = tile.bottom
        tile_sprite.name = tile.name
        all_sprites.append(tile_sprite)
    for enemy in room.enemies:
        all_sprites.append(enemy)
    all_sprites.append(player)
    update_all_sprites(all_sprites)
    for another_room in maze.rooms:
        another_room.last_visited += 1
    room.last_visited = 0
    room.visited = True

def maze_printable(func):
    def wrapper():
        print("")
        func()
        for i, room in enumerate(maze.rooms):
            if(i%maze.width == 0):
                print("")
            print(room, end= "")
            if i == room_number:
                print("*",end= "  ")
            elif room.no_skeletons == 1:
                print("s",end= "  ")
            elif room.no_skeletons == 2:
                print("ss",end= " ")
            elif room.skeleton_is_allowed():
                print(1,end= "  ")
            else:
                print(0,end= "  ")
        print(str(no_visited_rooms) + " / " + str(maze.size),end= " ")
        print(str(round(skeleton_chance(no_visited_rooms/maze.size)*100)) + "%")
        print(f"floor = {floor}")
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
    skeleton = Enemy("skeleton","variant_0",floor)
    skeleton.y = HEIGHT - 120 - skeleton.height/2
    for _ in range(1000):
        x = SCENE_WIDTH/2 + (SCENE_WIDTH/4-30)*(2*randint(0,1)-1)+randint(-(SCENE_WIDTH)/4+150,(SCENE_WIDTH)/4-150)
        skeleton.change_x(x)
        can_spawn = True
        for enemy in current_room().enemies:
            if iscolliding(skeleton,enemy,10):
                can_spawn = False
                break
        if can_spawn:
            break
    if can_spawn:
        current_room().enemies.append(skeleton)

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
        if(player.state in ["idle","running","jump"]):
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
                    build_room()
                    break
                elif(thing.name =="door" and number_of_chests == number_of_found_chests):
                    exit_game()
                    break
        elif(go_down and maze.rooms[room_number].south() == 1):
            for thing in player.colliding:
                if thing.name == "ladder":
                    sounds.ladder.ladder.play()
                    room_number += maze.width
                    build_room()
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
        build_room()
    elif(player.x > SCENE_WIDTH - player.hitbox.width*0.6 and maze.rooms[room_number].east() == 1):
        room_number += 1
        player.change_x(player.hitbox.width*0.61)
        build_room()

def entity_move():
    for sprite in all_sprites:
        if isinstance(sprite,Enemy):
            if (sprite.state == "die" and sprite.frame > 2
                and maze.rooms[room_number].has_closed_chest):
                open_chest(maze.get_chest_for(room_number))
            if sprite.is_dead:
                maze.rooms[room_number].enemies.remove(sprite)
                all_sprites.remove(sprite)
                maze.rooms[room_number].no_skeletons -= 1
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

def title_screen():
    global floor, game_ended
    game_ended = True
    background.image = "background/title"
    floor = 0
    player.health = 5
    for button in all_buttons:
        button.hide()
    play_button.show()
    for key in loot_collected.keys():
        loot_collected[key] = 0

def on_key_down():
    global go_down, go_up
    if player.can_move:
        if keyboard.up or keyboard.w:
            go_up = True
        elif keyboard.down or keyboard.s:
            go_down = True
    if player.state == "idle" or player.state == "running":
        if keyboard.lshift and jump_button.can_interact:
            player.change_state("jump")
        elif keyboard.lctrl and duck_button.can_interact:
            player.change_state("duck")
        elif keyboard.space and attack_button.can_interact:
            player.change_state("attack1")
    if keyboard.m:
        toggle_map()

def on_mouse_up():
    buttons_on("released")

def on_mouse_down(pos):
    if(mouse.LEFT):
        buttons_on("clicked")

def on_mouse_move(pos):
    move_mouse_hitbox(pos)

def move_mouse_hitbox(pos):
    mouse_hitbox.left = pos[0]-1
    mouse_hitbox.top = pos[1]-1

fingers = {}

def on_finger_down(event):
    x = event.x * HEIGHT
    y = event.y * WIDTH
    fingers[event.finger_id] = (x, y)
    move_mouse_hitbox((x,y))
    buttons_on("clicked")
    #print("touched at:",x,y)

def on_finger_up(event):
    pos = fingers.pop(event.finger_id, None)
    move_mouse_hitbox(pos)
    buttons_on("released")
    #print("released touch at:",event.finger_id)

def draw_sceen():
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
    if not game_ended:
        pygame.draw.rect(screen.surface, (58,58,58), ui_bar_left)
        pygame.draw.rect(screen.surface, (58,58,58), ui_bar_right)
        chest_icon.draw()
        for i in range(len(hearts)):
            if player.health > i:
                hearts[i].draw()
            else:
                hearts[i].lost.draw()
        for thing in loot_icons:
            thing.draw()
            screen.draw.text(str(loot_collected[thing.name]), midleft = (thing.pos[0] + thing.width/2, thing.pos[1]), color="white", fontsize=50)
        screen.draw.text(str(number_of_found_chests) + "/" + str(number_of_chests), center = chest_icon.pos, color="yellow", fontsize=50)
    for button in all_buttons:
        if button.is_visible:
            button.background.draw()
            button.draw()

load_mazes()
make_ui()
title_screen()

#show_hitboxes = True # for debugging only
def draw():
    screen.clear()
    background.draw()
    if not game_ended:
        draw_sceen()
        if map_open:
            maze_map.draw(maze,room_number)
    else:
        Actor("title",(WIDTH/2,HEIGHT/3)).draw()
    draw_ui()

def update():
    global dt
    dt = clock.tick(60)
    update_buttons()
    if not game_ended:
        pressing_up_or_down()
        change_player_speed()
        entity_move()
        animate_tiles()
        animate_entities()
        animate_loot()
        play_sounds()
        if player.is_dead:
            title_screen()

from pgzrun import run_mod
from pgzero.game import PGZeroGame
import sys

pgzero_game = None

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

async def main():
    pgzrun.go()
    await asyncio.sleep(0)

asyncio.run(main())