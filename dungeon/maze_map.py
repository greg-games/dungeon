from pgzero.actor import Actor
from line import Line
from constants import SCENE_WIDTH, HEIGHT, UI_BAR_WIDTH, WIDTH

map_background = Actor("map_background",(WIDTH/2,HEIGHT/2))

class MazeMap():
    def __init__(self,maze):
        self.lines = []
        self.scale = min((SCENE_WIDTH-120)/maze.width, (HEIGHT-120)/maze.height)//3
        for i, room in enumerate(maze.rooms):
            line = Line(
                room,self.scale,
                ((i%maze.width)*self.scale*3 + UI_BAR_WIDTH+90,
                 (i//maze.width)*self.scale*3 + self.scale*1.5+90))
            self.lines.append(line)

    def draw(self,maze):
        map_background.draw()
        for i, line in enumerate(self.lines):
            if maze.rooms[i].visited:
                line.draw()