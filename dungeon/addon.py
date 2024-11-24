import os
from pgzero.actor import Actor
from constants import *

class Addon(Actor):
    def __init__(self, name):
        self.name = name
        self.number_of_variants = len(os.listdir(f"images/tiles/addons/{name}")) - 1
        self.is_anim = False
        path = f"tiles/addons/{name}/variant_0"
        if(os.path.isdir(f"images/{path}")):
            self.is_anim = True
            path = f"{path}/default/0"
        addon_actor = Actor(path)
        width = addon_actor.width
        height = addon_actor.height
        with open(f"images/tiles/addons/{name}/properties.txt") as properties:
            for line in properties.readlines():
                prop, value = line.split("=")
                if "\"" in value:
                    self.__setattr__(prop.strip(),value.strip().strip("\"")) 
                else:
                    self.__setattr__(prop.strip(),eval(value.strip()))

all_addons = {Addon(addon_name) for addon_name in os.listdir(f"images/tiles/addons")}