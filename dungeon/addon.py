import os
from pgzero.actor import Actor
from constants import *

class Addon(Actor):

    def __init__(self, name):
        self.name = name
        self.number_of_variants = len(os.listdir(f"images/tiles/addons/{name}")) - 1
        max_number_on_screan = 0
        min_distance = 0
        x_start = 0
        x_end = 0
        y_start = 0
        y_end = 0

        constants = {name : value for (name, value) in globals().items() if name.isupper()}

        with open(f"images/tiles/addons/{name}/properties.txt") as properties:
            for line in properties.readlines():
                prop, value = line.split("=")
                if "\"" in value:
                    self.__setattr__(prop.strip(),value.strip()) 
                else:
                    value = value.strip()
                    for constant_name in constants.keys():
                        value = value.replace(constant_name,str(constants[constant_name]))
                    self.__setattr__(prop.strip(),eval(value))
all_addons = {Addon(addon_name) for addon_name in os.listdir(f"images/tiles/addons")}