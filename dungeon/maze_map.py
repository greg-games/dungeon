from pgzero.actor import Actor
from line import Line
from constants import SCENE_WIDTH, HEIGHT, UI_BAR_WIDTH, WIDTH

map_background = Actor("map_background",(WIDTH/2,HEIGHT/2))

class MazeMap():
    def __init__(self,maze):
        self.lines = []
        self.scale = min((SCENE_WIDTH-100)/(maze.width-(2/3)), (HEIGHT-86)/(maze.height-(2/3)))//3
        x_offset = (SCENE_WIDTH-100-((maze.width-(2/3))*self.scale*3))/2 + self.scale/2 + UI_BAR_WIDTH + 50
        y_offset = (HEIGHT-86-((maze.height-(2/3))*self.scale*3))/2 + self.scale/2 + 43
        for i, room in enumerate(maze.rooms):
            line = Line(
                room,i,self.scale+1,
                ((i%maze.width)*self.scale*3 + x_offset,
                 (i//maze.width)*self.scale*3 + y_offset))
            self.lines.append(line)

    def draw(self,maze,room_number):
        map_background.draw()
        for i, line in enumerate(self.lines):
            if maze.rooms[i].visited:
                line.draw(room_number)
