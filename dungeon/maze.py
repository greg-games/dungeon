from room import Room
from random import randrange, random

symbols = {
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

class Maze:
    def __init__(self, width:int, height:int, rooms:list):
        self.width = width
        self.height = height
        self.size = width * height
        if rooms == []:
            self.__generate()
        else:
            self.rooms = rooms
        self.__generate_distance()

    def __str__(self):
        maze_str = ""
        for i in range(self.height):
            for j in range(self.width):
                maze_str += symbols[tuple(self.rooms[i*self.width+j].exits)] + " "
            maze_str +=  "  ||  "
            if(2*i < self.height):
                for j in range(self.width):
                    maze_str += symbols[tuple(self.rooms[(2*i)*self.width+j].exits)]
            maze_str += "\n"
            for j in range(self.width): maze_str += "  "
            maze_str += "  ||  "
            if(2*i+1 < self.height):
                for j in range(self.width):
                    maze_str += symbols[tuple(self.rooms[(2*i+1)*self.width+j].exits)]
            maze_str += "\n"
        return f"\nWidth: {self.width}\nHeight: {self.height}\n{maze_str}"
    
    def __generate(self):
        self.rooms = [Room([0,0,0,0],0,[]) for i in range(self.size)]
        self.rooms[0].exits = [0,0,1,0]
        prev_dir, i = 2, 1
        self.__generate_next_tile(i,prev_dir)
        self.__make_loops()
    
    def __generate_distance(self):
        self.distance = [-1 for x in range(len(self.rooms))]
        next_tile = [(0,0)]
        while(len(next_tile) > 0):
            i, d = next_tile.pop(0)
            if(self.distance[i] == -1):
                self.distance[i] = d
                for j in range(4):
                    if(self.rooms[i].exits[j] == 1):
                        if(j%2 == 0):
                            next_tile.append((i+j-1,d+1))
                        else:
                            next_tile.append((i+(j-2)*self.width,d+1))
    
    def __generate_next_tile(self,i,prev_dir):
        go_to = 0
        self.rooms[i].exits[(prev_dir + 2) % 4] = 1
        available = self.__check_avaible(i, True)
        if len(available) > 0:
            go_to, new_dir = available[randrange(len(available))]
            self.rooms[i].exits[new_dir] = 1
            self.__generate_next_tile(go_to,new_dir)
            self.__generate_next_tile(i,prev_dir)

    def __check_avaible(self,i,empty):
        available = []
        for j in range(4):
            if(self.rooms[i].exits[j] == 0):
                if(j % 2 == 0):
                    next_tile = i + j - 1 #j - 1 = -1 lub 1
                    is_next_tile_in_maze = i%self.width + j - 1 >= 0 and i%self.width + j - 1 < self.width
                else:
                    next_tile = i + (j - 2)*self.width #j - 2 = -1 lub 1
                    is_next_tile_in_maze = next_tile < self.size

                if(is_next_tile_in_maze and next_tile > 0 
                   and (not empty or self.rooms[next_tile].exits == [0,0,0,0])):
                    available.append((next_tile,j))
        return available

    def __make_loops(self):
        for i in range(self.size//10):
            x = randrange(1,self.size)
            available = self.__check_avaible(x, False)
            for z in available:
                if(random() >= 0.5):
                    self.rooms[x].exits[z[1]] = 1
                    self.rooms[z[0]].exits[(z[1] + 2) % 4] = 1   
    
    def tiles_in_range(self,i,distance):
        tiles = [-1 for x in range(len(self.rooms))]
        next_tile = [(i,0)]
        while(len(next_tile) > 0):
            j, d = next_tile.pop(0)
            if(tiles[j] == -1 and d <= distance):
                self.rooms[j].is_chest_near = True
                for k in range(4):
                    if(self.rooms[j].exits[k] == 1):
                        if(k%2 == 0):
                            next_tile.append((j+k-1,d+1))
                        else:
                            next_tile.append((j+(k-2)*self.width,d+1))   
