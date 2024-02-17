from random import*

#WEST = 0
#NORTH = 1
#EAST = 2
#SOUTH = 3

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
    for i in range(maze_width*maze_height//15):
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
tuple([1,1,1,1]):"┼",
tuple([1,1,1,0]):"┴",
tuple([1,0,1,1]):"┬",
tuple([1,1,0,1]):"┤",
tuple([0,1,1,1]):"├",
tuple([1,1,0,0]):"┘",
tuple([0,1,1,0]):"└",
tuple([1,0,0,1]):"┐",
tuple([0,0,1,1]):"┌",
tuple([1,0,1,0]):"─",
tuple([0,1,0,1]):"│",
tuple([1,0,0,0]):"╸",
tuple([0,1,0,0]):"╹",
tuple([0,0,1,0]):"╺",
tuple([0,0,0,1]):"╻",
}

def print_maze(maze, maze_width, maze_height):
    print("")
    print("Width:", maze_width)
    print("Height:", maze_height)
    print("Maze number:", len(mazes))
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

ans = 0
while(ans != -2):
    ans = 0
    maze_width = int(input("set maze width to: "))
    maze_height = int(input("set maze height to: "))
    n = int(input("set number of mazes to: "))
    mazes = []
    for x in range(n):
        maze = generate_maze(maze_width,maze_height,True)
        print_maze(maze, maze_width, maze_height)
        mazes.append(maze)
    while(ans != -1 and ans != -2):
        ans = int(input("save maze number (to regenerate write -1, to end program write -2): "))
        if(ans < len(mazes) and ans >= 0):
            maze_rows = []
            for i in range(maze_height):
                maze_row = ""
                for j in range(maze_width):
                    maze_tile = symbols[tuple(mazes[ans][i*maze_width+j])]
                    maze_row += maze_tile
                    print(maze_tile, end="")
                print("")
                maze_rows.append(maze_row)
            if(input("Do you want to save maze number " + str(ans) + " (write 'yes' or 'no'): ") == "yes"):
                print("Saved maze number:",ans)
                file = open("labirynty.txt", "a", encoding="utf-8")
                file.write(str(maze_width))
                file.write("\n")
                file.write(str(maze_height))
                file.write("\n")
                for i in range(maze_height):
                    file.write(maze_rows[i])
                    file.write("\n")
                file.close()
        elif(ans != -1 and ans != -2):
            print("Incorect maze number")
print("Program ended")