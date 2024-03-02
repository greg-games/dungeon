import asyncio
import pgzrun
from random import*

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

maze_number = 6 #int(input("maze_number: "))
if maze_number == -1:
    maze_width = 10 #int(input("maze_width: "))
    maze_height = 5 #int(input("maze_height: "))
    maze = generate_maze(maze_width,maze_height,True)
else:
    maze = mazes[maze_number][0]
    maze_width = mazes[maze_number][1]
    maze_height = mazes[maze_number][2]
print_maze(maze, maze_width, maze_height)

maze[0] = [0,0,1,0]
WIDTH = 840
HEIGHT = 600
all_sprites = []
room_number = 0

player = Actor("alien")
player.pos = WIDTH/2,HEIGHT - 120 - player.height/2
PLAYER_SPEED = 7.5
player.speed = 0

player_colliding = []

def build_room(i):
    global all_sprites
    all_sprites = [] 
    y = 0
    for _ in range(2):
        x = 0
        for _ in range(2):
            for j in range(3):
                brick = Actor("cegła")
                brick.pos = brick.width*(j + 1/2) + x, brick.height/2 + y
                brick.name = "brick"
                all_sprites.append(brick)
            x = WIDTH/2 + brick.width/2
        y = HEIGHT - brick.height
    if(maze[i][0] == 0):
        for j in range(3):
            brick = Actor("cegła")
            brick.pos = brick.width/2 , brick.height * (3/2 + j)
            brick.name = "brick"
            all_sprites.append(brick)
    if(maze[i][1] == 0):
        brick = Actor("cegła")
        brick.pos = WIDTH/2, brick.height/2
        brick.name = "brick"
        all_sprites.append(brick)
    else:
        ladder = Actor("drabina")
        ladder.pos = WIDTH/2, ladder.height/2
        ladder.name = "ladder"
        all_sprites.append(ladder)
    if(maze[i][2] == 0):
        for j in range(3):
            brick = Actor("cegła")
            brick.pos = WIDTH - brick.width/2, brick.height * (3/2 + j)
            brick.name = "brick"
            all_sprites.append(brick)
    if(maze[i][3] == 0):
        brick = Actor("cegła")
        brick.pos = WIDTH/2, HEIGHT - brick.height/2
        brick.name = "brick"
        all_sprites.append(brick)
    else:
        ladder = Actor("drabina")
        ladder.pos = WIDTH/2, HEIGHT
        ladder.name = "ladder"
        all_sprites.append(ladder)     

def player_colide():
    global player_colliding
    player_colliding = []
    for sprite in all_sprites:
        if(player.right > sprite.left and player.left < sprite.right and player.top < sprite.bottom and player.bottom > sprite.top):
            player_colliding.append(sprite.name)

def player_move():
    global room_number
    global player_colliding
    player.x += player.speed
    player_colide()
    if "brick" in player_colliding:
        player.x -= player.speed
        player_colide()
    elif(player.x < player.width/2 and maze[room_number][0] == 1):
            room_number -= 1
            player.x = WIDTH - player.width/2
    elif(player.x > WIDTH - player.width/2 and maze[room_number][2] == 1):
            player.x = player.width/2
            room_number += 1

def on_key_down():
    global room_number
    if keyboard.up and "ladder" in player_colliding and maze[room_number][1] == 1:
        room_number -= maze_width
    elif keyboard.down and "ladder" in player_colliding and maze[room_number][3] == 1:
        room_number += maze_width

def draw():
    screen.clear()
    for sprite in all_sprites:
        sprite.draw()
    player.draw()

def update():
    player_colide()
    player.speed = 0
    if keyboard.left:
        player.speed = -1*PLAYER_SPEED
    elif keyboard.right:
        player.speed = PLAYER_SPEED
    player_move()
    build_room(room_number)

async def main():
    pgzrun.go()
    await asyncio.sleep(0)

asyncio.run(main())