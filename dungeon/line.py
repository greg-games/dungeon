import pygame

from pygame import Rect

class Line:
    def __init__(self,room,room_number,scale,pos):
        shapes = [
            Rect((pos[0] - scale*3/2),(pos[1] - scale/2),scale,scale),
            Rect((pos[0] - scale/2),(pos[1] - scale*3/2),scale,scale),
            Rect((pos[0] + scale/2),(pos[1] - scale/2),scale,scale),
            Rect((pos[0] - scale/2),(pos[1] + scale/2),scale,scale),
        ]
        self.shape = [Rect((pos[0] - scale/2),(pos[1] - scale/2),scale,scale)]
        self.room_number = room_number
        self.scale = scale
        self.pos = pos
        for i in range(4):
            if room.exits[i]:
                  self.shape.append(shapes[i])

    def draw(self,room_number):
        for shape in self.shape:
            pygame.draw.rect(screen.surface, "black", shape)
        if(room_number ==  self.room_number):
            pygame.draw.circle(screen.surface, "red", self.pos, self.scale/3)