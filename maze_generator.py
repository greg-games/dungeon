from random import*

WEST = 0
NORTH = 1
EAST = 2
SOUTH = 3

def generate_next_tile(i,prev_dir,maze,maze_width,maze_height):
    go_to = 0
    maze[i][(prev_dir + 2) % 4] = 1
    available = []
    if((i%maze_width) + 1 < maze_width):
        if(maze[i + 1] == [0,0,0,0]):
            available.append((i + 1,EAST))
            if(prev_dir != EAST):
                available.append((i + 1,EAST))
            else:
                available.append((i + 1,EAST))
                available.append((i + 1,EAST))
    if((i%maze_width) - 1 >= 0):
        if(maze[i - 1] == [0,0,0,0]):
            available.append((i - 1,WEST))
            if(prev_dir != WEST):
                available.append((i - 1,WEST))
            else:
                available.append((i - 1,WEST))
                available.append((i - 1,WEST))
    if(i + maze_width < maze_width*maze_height):
        if(maze[i + maze_width] == [0,0,0,0]):
            available.append((i + maze_width,SOUTH))
            if(prev_dir != SOUTH):
                available.append((i + maze_width,SOUTH))
    if(i - maze_width >= 0):
        if(maze[i - maze_width] == [0,0,0,0]):
            available.append((i - maze_width,NORTH))
            if(prev_dir != NORTH):
                available.append((i - maze_width,NORTH))
    if len(available) > 0:
        go_to, new_dir = available[randrange(len(available))]
        maze[i][new_dir] = 1
        generate_next_tile(go_to,new_dir,maze,maze_width,maze_height)
        generate_next_tile(i,prev_dir,maze,maze_width,maze_height)

def make_loops(maze,maze_width,maze_height):
    for i in range(maze_width*maze_height//15):
        x = randrange(1,maze_width*maze_height)
        available = []
        for j in range(4):
            if(maze[x][j] == 0):
                if(j % 2 == 0):
                    if((x%maze_width) + j - 1 >= 0 and (x%maze_width) + j - 1 < maze_width):
                        available.append((x + j - 1,j))
                elif(x + (j - 2)*maze_width < maze_width*maze_height and x + (j - 2)*maze_width >= 0):
                    available.append((x + (j - 2)*maze_width,j))
        for z in available:
            if(random() >= 0.5):
                maze[x][z[1]] = 1
                maze[z[0]][(z[1] + 2) % 4] = 1



        

def generate_maze(maze_width,maze_height,loops: bool):
    maze = [[0,0,0,0] for i in range(maze_width*maze_height)]
    maze[0] = "s"
    prev_dir = EAST
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