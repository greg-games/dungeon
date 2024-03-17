class Room:    
    def __init__(self, exits:list,distance:int, tiles:list):
        self.exits = exits
        self.distance = distance
        self.tiles = tiles
        self.is_chest_near = False
        self.has_chest = False
        self.door_index = -1
        self.chest_index = -1
        self.north_ladder_index = -1
        self.south_ladder_index = -1
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
        return min(self.distance//7,3)
    def chest_is_allowed(self, max_allowed_distance):
        return (self.distance > 7 and 
           not self.is_chest_near and
           self.distance*2 < max_allowed_distance)
    def chest(self):
        return self.tiles[self.chest_index]