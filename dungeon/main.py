import asyncio
import pgzrun
from random import*

WEST = 0
NORTH = 1
EAST = 2
SOUTH = 3

def generate_next_tile(i,prev_dir,maze,maze_width,maze_height):
    go_to = 0
    maze[i][(prev_dir + 2) % 4] = 1
    available = check_avaible(i, maze, maze_width, maze_height, True)
    if len(available) > 0:
        go_to, new_dir = available[randrange(len(available))]
        maze[i][new_dir] = 1
        generate_next_tile(go_to,new_dir,maze,maze_width,maze_height)
        generate_next_tile(i,prev_dir,maze,maze_width,maze_height)

def check_avaible(i, maze, maze_width, maze_height, empty):
    available = []
    for j in range(4):
        if(maze[i][j] == 0):
            if(j % 2 == 0):
                next_tile = i + j - 1 #j - 1 = -1 lub 1
                if(i%maze_width + j - 1 >= 0 and i%maze_width + j - 1 < maze_width
                    and (not empty or maze[next_tile] == [0,0,0,0]) and maze[next_tile] != 's'):
                    for x in range(2):
                        available.append((next_tile,j))
            else:
                next_tile = i + (j - 2)*maze_width #j - 2 = -1 lub 1
                if(next_tile < maze_width*maze_height and next_tile >= 0
                   and (not empty or maze[next_tile] == [0,0,0,0]) and maze[next_tile] != 's'):
                    available.append((next_tile,j))
    return available

def make_loops(maze,maze_width,maze_height):
    for i in range(maze_width*maze_height//10):
        x = randrange(1,maze_width*maze_height)
        available = check_avaible(x, maze, maze_width, maze_height, False)
        for z in available:
            if(random() >= 0.5):
                maze[x][z[1]] = 1
                maze[z[0]][(z[1] + 2) % 4] = 1

def generate_maze(maze_width,maze_height,loops: bool):
    maze = [[0,0,0,0] for i in range(maze_width*maze_height)]
    maze[0] = "s"
    prev_dir = 2
    i = 1
    generate_next_tile(i,prev_dir,maze,maze_width,maze_height)
    if loops: make_loops(maze,maze_width,maze_height)
    return maze

symbols = {
tuple("s"):"s",
(1,1,1,1):"┼",
(1,1,1,0):"┴",
(1,0,1,1):"┬",
(1,1,0,1):"┤",
(0,1,1,1):"├",
(1,1,0,0):"┘",
(0,1,1,0):"└",
(1,0,0,1):"┐",
(0,0,1,1):"┌",
(1,0,1,0):"─",
(0,1,0,1):"│",
(1,0,0,0):"╸",
(0,1,0,0):"╹",
(0,0,1,0):"╺",
(0,0,0,1):"╻",
}
symbols2 = {
"s":"s",
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

def print_maze(maze, maze_width, maze_height):
    print("")
    print("Width:", maze_width)
    print("Height:", maze_height)
    for i in range(maze_height):
        for j in range(maze_width):
            print(symbols[tuple(maze[i*maze_width+j])], end=" ")
        print("  ||  ", end="")
        if(2*i < maze_height):
            for j in range(maze_width):
                print(symbols[tuple(maze[(2*i)*maze_width+j])], end="")
        print("")
        for j in range(maze_width): print(" ", end=" ")
        print("  ||  ", end="")
        if(2*i+1 < maze_height):
            for j in range(maze_width):
                print(symbols[tuple(maze[(2*i+1)*maze_width+j])], end="")
        print("")

file = open("labirynty.txt", "r", encoding="utf-8")
lines = file.readlines()
x = 0
mazes = []
while x < len(lines):
    maze = []
    maze_width = int(lines[x])
    x += 1
    maze_height = int(lines[x])
    for i in range(maze_height):
        x += 1
        line = lines[x]
        for j in range(maze_width):
            maze.append(symbols2[line[j]])
    mazes.append((maze, maze_width, maze_height))
    x += 1

def generate_maze_distance(maze_width):
    maze[0] = (0,0,1,0)
    maze_distance = [-1 for x in range(len(maze))]
    next_tile = [(0,0)]
    while(len(next_tile) > 0):
        i, d = next_tile.pop(0)
        if(maze_distance[i] == -1):
            maze_distance[i] = d
            for j in range(4):
                if(maze[i][j] == 1):
                    if(j%2 == 0):
                        next_tile.append((i+j-1,d+1))
                    else:
                        next_tile.append((i+(j-2)*maze_width,d+1))
    return maze_distance

TITLE = "Greg Games - Dungeon"
WIDTH = 840
HEIGHT = 600

NO_VARIANT = -1

game_ended = False

player = Actor("alien")
player.pos = WIDTH/2,HEIGHT - 120 - player.height/2
PLAYER_SPEED = 7.5
player.speed = 0

chest_icon = Actor("chest icon")
chest_icon.pos = (chest_icon.width,chest_icon.height)

def set_up_game():
    global game_ended
    global maze_number
    global maze
    global maze_width
    global maze_height
    global maze_distance
    global room_number
    global all_sprites
    global player_colliding
    global number_of_chests
    global number_of_found_chests

    game_ended = False

    maze_number = -1 #int(input("maze_number: "))
    if maze_number == -1:
        maze_width = randint(10,13)#10 #int(input("maze_width: "))
        maze_height = randint(4,6)#5 #int(input("maze_height: "))
        maze = generate_maze(maze_width,maze_height,True)
    else: 
        maze = mazes[maze_number][0]
        maze_width = mazes[maze_number][1]
        maze_height = mazes[maze_number][2]
    print_maze(maze, maze_width, maze_height)
    maze_distance = generate_maze_distance(maze_width)

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

class Room:
    def __init__(self, exits:tuple,distance:int, tiles:list):
        self.exits = exits
        self.west = exits[0]
        self.north = exits[1]
        self.east = exits[2]
        self.south = exits[3]
        self.distance = distance
        self.tiles = tiles
        self.is_chest_near = False

    def no_of_exits(self):
        return sum(self.exits)

class Tile:
    def __init__(self, name:str, variant:int, pos:tuple):
        self.name = name
        self.variant = variant
        self.pos = pos
    def image(self):
        if self.variant == NO_VARIANT:
            return self.name
        return self.name+"/"+str(self.variant)

class Chest(Tile):
    def __init__(self, name:str, variant:int, x:int, is_open:bool):
        self.is_open = is_open
        self.bottom = HEIGHT - Actor("brick/0").height
        self.frame = 0
        super().__init__(name, variant, (x,self.bottom + Actor("chest/0/0").height/2))
    def image(self):
        return self.name+"/"+str(self.variant)+"/"+str(self.frame)
    
    

class Addon:
    def __init__(self, name:str, number_of_variants:int, max_number_on_screan:int,min_distance:int, 
                 can_collide:tuple, x_start:int, x_end:int, y_start:int, y_end:int):
        self.name = name
        self.number_of_variants = number_of_variants
        self.max_number_on_screan = max_number_on_screan
        self.min_distance = min_distance
        self.can_collide = can_collide
        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end

    def image(self,variant):
        if variant == NO_VARIANT:
            return self.name
        return self.name+"/"+str(variant)   

def make_tiles():
    maze[0] = Room((0,0,1,0),0,[])
    for i in range(len(maze)):
        if(i > 0):
            maze[i] = Room(tuple(maze[i]),maze_distance[i],[])
        make_room_frame(i)
        make_addons(i)
        make_chests(i)
    add_more_chests()

def make_room_frame(i):
    brick = Actor("brick/0")
    ladder = Actor("ladder")
    for x in range(5):
        for y in range(3):
            maze[i].tiles.append(Tile("background",NO_VARIANT,(brick.width*(x + 3/2), brick.height*(y + 3/2))))
    y = 0
    for _ in range(2):
        x = 0
        for _ in range(2):
            for j in range(3):
                maze[i].tiles.append(Tile("brick",randint(0,7),(brick.width*(j + 1/2) + x, brick.height/2 + y)))
            x = WIDTH/2 + brick.width/2
        y = HEIGHT - brick.height
    if(maze[i].west == 0):
        name, variant = "brick", randint(0,7)
    else:
        name, variant = "background", NO_VARIANT
    for j in range(3):
        maze[i].tiles.append(Tile(name,variant,(brick.width/2 , brick.height * (3/2 + j))))
    
    if(maze[i].north == 0):
        maze[i].tiles.append(Tile("brick",randint(0,7),(WIDTH/2, brick.height/2)))
    else:
        maze[i].tiles.append(Tile("background",NO_VARIANT,(WIDTH/2, brick.height/2)))
        maze[i].tiles.append(Tile("ladder",NO_VARIANT,(WIDTH/2, ladder.height/2)))
    
    if(maze[i].east == 0):
        name, variant = "brick", randint(0,7)
    else:
        name, variant = "background", NO_VARIANT
    for j in range(3):
        maze[i].tiles.append(Tile(name, variant,(WIDTH - brick.width/2, brick.height * (3/2 + j))))
    
    if(maze[i].south == 0):
        maze[i].tiles.append(Tile("brick",randint(0,7),(WIDTH/2, HEIGHT - brick.height/2)))
    else:
        maze[i].tiles.append(Tile("background",NO_VARIANT,(WIDTH/2, HEIGHT - brick.height/2)))
        maze[i].tiles.append(Tile("ladder",NO_VARIANT,(WIDTH/2, HEIGHT)))

def make_addons(i):
    crack = Actor("crack")
    all_addons = [ #(name, number of variants, max number on screan, min distance, can_collide, x start, x end, y start, y end)
        Addon("torch",0,2,200,("background"),WIDTH/10, WIDTH*9/10, HEIGHT/2, HEIGHT/2),
        Addon("crack",0,3,100,("background"),crack.width/2, WIDTH - crack.width/2, HEIGHT/10, HEIGHT*7/8),
        Addon("crack",0,3,100,("brick"),crack.width/2, WIDTH - crack.width/2, HEIGHT/10, HEIGHT*7/8)
    ]
    if(i == 0):
        maze[i].tiles.append(Tile("door",NO_VARIANT,(WIDTH/2,HEIGHT - 120 - Actor("door").height/2)))
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
                    for tile in maze[i].tiles:
                        distance = 0
                        if(tile.name == addon.name):
                            distance = addon.min_distance
                        if(not tile.name in addon.can_collide and
                               iscolliding(Actor(addon.image(variant),pos),Actor(tile.image(),tile.pos),distance)): 
                            pos_avaible = False
                            break
                    counter += 1
                if pos_avaible:
                    maze[i].tiles.append(Tile(addon.name,variant,pos))

def make_chests(i):
    global number_of_chests
    if(maze[i].no_of_exits() == 1 and i != 0):
        chest_type = 0
        for j in range(1,4):
            if(maze[i].distance > j*7): chest_type += 1
        x = WIDTH*(randint(0,1)*2+1)/4
        if(maze[i].east == 1):
            x = WIDTH/4
        elif(maze[i].west == 1):
            x = WIDTH*3/4
        maze[i].tiles.append(Chest("chest",chest_type,x,False))
        number_of_chests += 1
    


def add_more_chests():
    global number_of_chests
    for i in range(len(maze)):
        for tile in maze[i].tiles:
            if isinstance(tile,Chest):
                tiles_in_range(i,3)
                break
    print("")
    for i in range(len(maze)):
        if(maze[i].distance > 7 and 
           not maze[i].is_chest_near and
           maze[i].distance*2 < randrange(maze_width*maze_height)):
            chest_type = 0
            for j in range(1,4):
                if(maze[i].distance > j*7): chest_type += 1
            x = WIDTH*(randint(0,1)*2+1)/4
            if(maze[i].north != 1 and maze[i].south != 1):
                x = WIDTH/2
            if(chest_type > 0): chest_type -= 1
            maze[i].tiles.append(Chest("chest",chest_type,x,False))
            number_of_chests += 1
            tiles_in_range(i,3)
    print(number_of_chests)


def tiles_in_range(i,distance):
    tiles = [-1 for x in range(len(maze))]
    next_tile = [(i,0)]
    while(len(next_tile) > 0):
        j, d = next_tile.pop(0)
        if(tiles[j] == -1 and d <= distance):
            maze[j].is_chest_near = True
            for k in range(4):
                if(maze[j].exits[k] == 1):
                    if(k%2 == 0):
                        next_tile.append((j+k-1,d+1))
                    else:
                        next_tile.append((j+(k-2)*maze_width,d+1))   

def build_room(i):
    global all_sprites
    all_sprites = []
    for tile in maze[i].tiles:
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
    elif(player.x < player.width/2 and maze[room_number].west == 1):
            room_number -= 1
            player.x = WIDTH - player.width/2
            build_room(room_number)
    elif(player.x > WIDTH - player.width/2 and maze[room_number].east == 1):
            player.x = player.width/2
            room_number += 1
            build_room(room_number)

def animate_chests():
    chests = [tile for tile in maze[room_number].tiles if isinstance(tile,Chest)]
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
            if("ladder" in player_colliding and maze[room_number].north == 1):
                room_number -= maze_width
                build_room(room_number)
            elif("door" in player_colliding):
                exit_game()
        elif(keyboard.down and "ladder" in player_colliding and maze[room_number].south == 1):
            room_number += maze_width
            build_room(room_number)
    elif keyboard.escape: set_up_game()

def on_mouse_down():
    global number_of_found_chests
    chests = [tile for tile in maze[room_number].tiles if isinstance(tile,Chest)]
    if(mouse.LEFT and any(chests)):
        for chest in chests:
            if(iscolliding(player,Actor(chest.image(),chest.pos),150) and
               not chest.is_open):
                chest.is_open = True
                number_of_found_chests += 1

set_up_game()

def draw():
    screen.clear()
    for sprite in all_sprites:
        sprite.draw()
    player.draw()
    chest_icon.draw()
    #screen.draw.text(str(number_of_found_chests) + "/" + str(number_of_chests), center = chest_icon.pos, color="yellow", fontsize=50)

def update():
    if not game_ended:
        player.speed = 0
        if keyboard.left:
            player.speed -= PLAYER_SPEED
        if keyboard.right:
            player.speed += PLAYER_SPEED
        player_move()
        player_colide()
        animate_chests()   

async def main():
    pgzrun.go()
    await asyncio.sleep(0)

asyncio.run(main())
