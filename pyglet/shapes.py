import pyglet
import webcolors
import palettable
import random
import math

from ray import scale_color

rainbowquad = pyglet.graphics.vertex_list(4,
    ('v2i', (10, 10,  100, 10, 100, 100, 10, 100)),
    ('c3B', (255, 255, 255,
             0, 0, 255,
             0, 255, 0,
             255, 0, 0)))

class ShapeDrawer(object):

    def __init__(self, base_size=100):
        self.base_size = base_size

    def get_monocolored_arg(self, color, points):
        ret = [*color]
        if points > 1:
            for x in range(points-1):
                ret.extend(color)
        return ('c3B', tuple(ret))

    def get_colored_arg(self, color, points, color_dict):
        ret = []
        for x in range(points):
            if x in color_dict:
                ret.extend(scale_color(color_dict[x]))
            else:
                ret.extend(color)
        # this results in some grossness for circles at least
        return ('c3B', tuple(ret))

    def draw(self, shape):
        coords = self.get_coords(shape)
        colors = self.get_monocolored_arg(shape.color, int(len(coords[1])/2))
        pyglet.graphics.vertex_list(int(len(coords[1])/2),
            coords, colors ).draw(self.draw_mode)

class Triangle(ShapeDrawer):

    def __init__(self, base_size):
        super().__init__(base_size)
        self.points = 3
        self.draw_mode = pyglet.gl.GL_TRIANGLES

    def get_coords(self, shape):
        center = shape.center
        size = self.base_size+shape.scale
        bottom_left = (int(center[0]-size/2), int(center[1]-size/2))
        bottom_right = (int(center[0]+size/2), int(center[1]-size/2))
        top = (int(center[0]), int(center[1]+size/2))
        return ('v2i', (*bottom_left, *bottom_right, *top))

class Circle(ShapeDrawer):

    def __init__(self, base_size, points=365):
        super().__init__(base_size)
        self.radius = self.base_size / 2
        self.points = points
        self.draw_mode = pyglet.gl.GL_POLYGON

    def get_coords(self, shape):
        points = []
        center = shape.center
        step = math.ceil(365 / self.points)
        for i in range(0, 365, step): # should be a range to 365 taking n steps where n is self.points
            points.append(round(self.radius * math.sin(i),3)+center[0])
            points.append(round(self.radius * math.cos(i),3)+center[1])

        points = [point for point in points]
        return ('v2f', tuple(points))

class Square(ShapeDrawer):

    def __init__(self, base_size):
        super().__init__(base_size)
        self.points = 4
        self.draw_mode = pyglet.gl.GL_QUADS

    def get_coords(self, shape):
        center = shape.center
        size = self.base_size+shape.scale
        bottom_left = (int(center[0]-size/2), int(center[1]-size/2))
        bottom_right = (int(center[0]+size/2), int(center[1]-size/2))
        top_left = (int(center[0]-size/2), int(center[1]+size/2))
        top_right = (int(center[0]+size/2), int(center[1]+size/2))
        return ('v2i', (*bottom_left, *bottom_right, *top_right, *top_left))

class Heart(ShapeDrawer):

    def __init__(self, base_size):
        super().__init__(base_size)
        self.points = 6
        self.draw_mode = pyglet.gl.GL_POLYGON

    def get_coords(self, shape):
        #.....5..........3.....
        #6....................2
        #..........4...........
        #......................
        #..........1...........
        #4 = c
        center = shape.center
        size = self.base_size+shape.scale
        point1 = (int(center[0]), int(center[1]-size/2))
        point2 = (int(center[0]+size/2), int(center[1]+size/4))
        point3 = (int(center[0]+size/4), int(center[1]+size/2))
        point4 = center
        point5 = (int(center[0]-size/4), int(center[1]+size/2))
        point6 = (int(center[0]-size/2), int(center[1]+size/4))
        return ('v2i', (*point1, *point2, *point3, *point4, *point5, *point6))

class Shape(object):
    def __init__(self, scale=1, color = None, center=(400, 400)):
        self.scale = scale
        self.color = color or self.random_color()
        self.center = center

    def random_color(self, pallete=palettable.colorbrewer.qualitative.Paired_12, span=12):
        return pallete.colors[random.randrange(0,span)]


class ShapeManager(object):
    def __init__(self):
        self.shapes = [Shape()]

    def loop(self):
        new_shapes = [Shape()]
        for sh in self.shapes:
            if sh.scale < 800:
                sh.scale = sh.scale + 20
                new_shapes.append(sh)
        self.shapes = new_shapes


class RepeatingShape(object):

    def __init__(self, drawer=Circle):
        self.sm = ShapeManager()
        self.drawer = drawer()
        self.drawer2 = Square()

    def draw(self):
        self.sm.loop()
        for sh in reversed(self.sm.shapes):
            #self.drawer2.draw(sh)
            self.drawer.draw(sh)



if __name__ == "__main__":
    window = pyglet.window.Window(height=800, width=800)
    rs = RepeatingShape()
    @window.event
    def on_draw(*args):
        window.clear()
        rs.draw()
    pyglet.clock.schedule_interval(on_draw, 0.01)
    pyglet.app.run()

