from random import random

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
        self.chests_in_range = 0
        self.is_chest_in_range = False
        self.is_max_skeletons_in_range = False
        self.no_skeletons = 0
        self.skeletons_chance = 0
        self.north_ladder_index = -1
        self.south_ladder_index = -1
        self.animated_tiles_indexes = []
    
    def __str__(self):
        return symbols[tuple(self.exits)]

    def no_of_exits(self):
        return sum(self.exits)
    def west(self):
        return self.exits[0]
    def north(self):
        return self.exits[1]
    def east(self):
        return self.exits[2]
    def south(self):
        return self.exits[3]
    def set_distance(self,distance):
        self.distance = distance
    def chest_type(self):
        return min(self.distance//7, 3)
    def chest_is_allowed(self, max_allowed_distance):
        return (self.distance > 7 and 
           not self.is_chest_in_range and
           self.distance*2 < max_allowed_distance)
    def animated_tile(self,i):
        return self.tiles[self.animated_tiles_indexes[i]]