from pgzero.actor import Actor

class Addon(Actor):
    def __init__(self, name:str, number_of_variants:int, max_number_on_screan:int,min_distance:int, 
                 x_start:int, x_end:int, y_start:int, y_end:int):
        self.name = name
        self.number_of_variants = number_of_variants
        self.max_number_on_screan = max_number_on_screan
        self.min_distance = min_distance
        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end