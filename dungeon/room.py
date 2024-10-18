from tile import Chest
from constants import SCENE_WIDTH
from random import randint

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

class Room:
    def __init__(self, exits:list,distance:int, tiles:list):
        self.exits = exits
        self.distance = distance
        self.tiles = tiles
        self.tiles_names = [tile.name for tile in tiles]
        self.chests_in_range = 0
        self.is_chest_in_range = False
        self.has_closed_chest = False
        self.no_skeletons = 0
        self.last_visited = 0
        self.rooms_in_range = []
        self.north_ladder_index = -1
        self.south_ladder_index = -1
        self.animated_tiles_indexes = []
        self.enemies = []
        self.visited = False

    def __str__(self):
        return symbols[tuple(self.exits)]

    def no_of_exits(self):
        return sum(self.exits)
    def west(self):
        return self.exits[0] == 1
    def north(self):
        return self.exits[1] == 1
    def east(self):
        return self.exits[2] == 1
    def south(self):
        return self.exits[3] == 1
    def is_dead_end(self):
        return self.no_of_exits() == 1
    def set_distance(self,distance):
        self.distance = distance
    def chest_type(self,difficulty):
        chest_type = min(self.distance//7,min(difficulty//3+1, 3))
        if self.no_of_exits() > 1:
            chest_type -= 1
        return chest_type
    def chest_is_allowed(self, max_allowed_distance):
        return (self.distance > 7 and 
                not self.is_chest_in_range and
                self.distance*2 < max_allowed_distance)
    def skeleton_is_allowed(self):
        return (self.distance != 0 and 
                self.no_skeletons == 0 and 
                self.last_visited > 7)
    def animated_tile(self,i):
        return self.tiles[self.animated_tiles_indexes[i]]
    def tiles_add(self,tile):
        self.tiles.append(tile)
        self.tiles_names.append(tile.name)

    def add_chest(self, difficulty):
        x = SCENE_WIDTH*(randint(0,1)*2+1)/4
        if self.is_dead_end():
            if(self.east()):
                x = SCENE_WIDTH/4
            elif(self.west()):
                x = SCENE_WIDTH*3/4
        elif(not self.north() and not self.south()):
            x = SCENE_WIDTH/2
        self.tiles_add(Chest("chest",self.chest_type(difficulty),x))
        self.animated_tiles_indexes.append(len(self.tiles) - 1)
        self.has_closed_chest = True