import pyglet
import webcolors
import palettable
import random



window = pyglet.window.Window(height=800, width=800)



rainbowquad = pyglet.graphics.vertex_list(4,
    ('v2i', (10, 10,  100, 10, 100, 100, 10, 100)),
    ('c3B', (255, 255, 255,
             0, 0, 255,
             0, 255, 0,
             255, 0, 0)))




class Shape(object):
    def __init__(self, scale, color = None, center=(400, 400)):
        self.scale = scale
        self.color = color or self.random_color()
        self.center = center

    def random_color(self, pallete=palettable.colorbrewer.qualitative.Paired_12, span=12):
        return pallete.colors[random.randrange(0,span)]

    def get_monocolored_arg(self, color, points):
        ret = [*color]
        if points > 1:
            for x in range(points-1):
                ret.extend(color)
        return ('c3B', tuple(ret))

    def draw(self):
        pass

class Square(Shape):

    def get_coords(self, scale):
        scaled = scale*10
        center = self.center
        size = 100+scale
        bottom_left = (int(center[0]-size/2), int(center[0]-size/2))
        bottom_right = (bottom_left[0]+size, bottom_left[1])
        top_right = (bottom_left[0]+size, bottom_left[1]+size)
        top_left = (bottom_left[0], bottom_left[1]+size)
        return ('v2i', (*bottom_left, *bottom_right, *top_right, *top_left))

    def draw(self):
        pyglet.graphics.vertex_list(4,
            self.get_coords(self.scale),
            self.get_monocolored_arg(self.color, 4)
                     ).draw(pyglet.gl.GL_QUADS)

class ShapeManager(object):
    def __init__(self, shape=Shape):
        self.shape = shape
        self.shapes = [self.shape(1)]

    def loop(self):
        new_shapes = [self.shape(1)]
        for sh in self.shapes:
            if sh.scale < 600:
                sh.scale = sh.scale + 20
                new_shapes.append(sh)
        self.shapes = new_shapes


class RepeatingShape(object):

    def __init__(self, shape=Square):
        self.sm = ShapeManager(shape)

    def draw(self):
        self.sm.loop()
        for sh in reversed(self.sm.shapes):
            sh.draw()

rs = RepeatingShape()
@window.event
def on_draw(*args):
    window.clear()
    rs.draw()


if __name__ == "__main__":
    pyglet.clock.schedule_interval(on_draw, 0.01)
    pyglet.app.run()

