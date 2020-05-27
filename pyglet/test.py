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

class ShapeDrawer(object):

    def __init__(self):
        self.base_size = 100

    def get_monocolored_arg(self, color, points):
        ret = [*color]
        if points > 1:
            for x in range(points-1):
                ret.extend(color)
        return ('c3B', tuple(ret))

    def draw(self, shape):
        pyglet.graphics.vertex_list(self.points,
            self.get_coords(shape),
            self.get_monocolored_arg(shape.color, self.points)
                     ).draw(self.draw_mode)

class Triangle(ShapeDrawer):

    def __init__(self):
        super().__init__()
        self.base_size = 150
        self.points = 3
        self.draw_mode = pyglet.gl.GL_TRIANGLES

    def get_coords(self, shape):
        center = shape.center
        size = self.base_size+shape.scale
        bottom_left = (int(center[0]-size/2), int(center[0]-size/2))
        bottom_right = (int(center[0]+size/2), int(center[0]-size/2))
        top = (int(center[0]), int(center[0]+size/2))
        return ('v2i', (*bottom_left, *bottom_right, *top))


class Square(ShapeDrawer):

    def __init__(self):
        super().__init__()
        self.points = 4
        self.draw_mode = pyglet.gl.GL_QUADS

    def get_coords(self, shape):
        center = shape.center
        size = self.base_size+shape.scale
        bottom_left = (int(center[0]-size/2), int(center[0]-size/2))
        bottom_right = (int(center[0]+size/2), int(center[0]-size/2))
        top_left = (int(center[0]-size/2), int(center[0]+size/2))
        top_right = (int(center[0]+size/2), int(center[0]+size/2))
        return ('v2i', (*bottom_left, *bottom_right, *top_right, *top_left))

    def draw(self, shape):
        pyglet.graphics.vertex_list(4,
            self.get_coords(shape),
            self.get_monocolored_arg(shape.color, 4)
                     ).draw(pyglet.gl.GL_QUADS)

class Heart(ShapeDrawer):

    def __init__(self):
        super().__init__()
        self.points = NAN
        self.draw_mode = pyglet.gl.GL_POLYGON

    def get_coords(self, shape):
        center = shape.center
        size = self.base_size+shape.scale
        top = (int(center[0]), int(center[0]+size/2))
        return ('v2i', (*bottom_left, *bottom_right, *top_right, *top_left))

    def draw(self, shape):
        pyglet.graphics.vertex_list(4,
            self.get_coords(shape),
            self.get_monocolored_arg(shape.color, 4)
                     ).draw(pyglet.gl.GL_POLYGON)


class Shape(object):
    def __init__(self, scale, color = None, center=(400, 400)):
        self.scale = scale
        self.color = color or self.random_color()
        self.center = center

    def random_color(self, pallete=palettable.colorbrewer.qualitative.Paired_12, span=12):
        return pallete.colors[random.randrange(0,span)]


    def draw(self):
        pass

class ShapeManager(object):
    def __init__(self):
        self.shapes = [Shape(1)]

    def loop(self):
        new_shapes = [Shape(1)]
        for sh in self.shapes:
            if sh.scale < 800:
                sh.scale = sh.scale + 20
                new_shapes.append(sh)
        self.shapes = new_shapes


class RepeatingShape(object):

    def __init__(self, drawer=Triangle):
        self.sm = ShapeManager()
        self.drawer = drawer()
        self.drawer2 = Square()

    def draw(self):
        self.sm.loop()
        for sh in reversed(self.sm.shapes):
            #self.drawer2.draw(sh)
            self.drawer.draw(sh)

rs = RepeatingShape()
@window.event
def on_draw(*args):
    window.clear()
    rs.draw()


if __name__ == "__main__":
    pyglet.clock.schedule_interval(on_draw, 0.01)
    pyglet.app.run()

