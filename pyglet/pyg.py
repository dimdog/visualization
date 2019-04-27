import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet import clock
import colour
from math import radians, sin, cos

from audioprocessor import AudioProcessor
from body import Body


WIDTH = 1280
HEIGHT = 780

window = pyglet.window.Window(WIDTH, HEIGHT, vsync=False)
b = Body(WIDTH/2, HEIGHT/2, 20)
# TODO create rebroadcaster bodies
a = AudioProcessor(b)

class BodyManager(object):

    def __init__(self, *bodies):
        self.bodies = bodies

    def gen_vertex_list(self):
        ray_coords = []
        ray_colors = []
        for b in self.bodies:
            ray_coords.extend(b.ray_coords)
            ray_colors.extend(b.ray_colors)

        self.vertex_list = pyglet.graphics.vertex_list(int(len(ray_coords) / 2),
                        ('v2f', ray_coords),
                        ('c3B', ray_colors))

    def update_vertex_lists(self, *args):
        for b in self.bodies:
            b.update_vertex_list()
        self.gen_vertex_list()


bm = BodyManager(b)
clock.schedule(bm.update_vertex_lists) # remember this can take a delay
# schedule something that resets the color range every ... ???

@window.event
def on_draw():
    window.clear()
    if bm.vertex_list:
        bm.vertex_list.draw(pyglet.gl.GL_LINES)

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.A:
        print("AAAA YOOO")
    if symbol == key.C and modifiers == 2:
        window.close()
    if symbol == key.R:
        a.reset()

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        print('The left mouse button was pressed.')

pyglet.app.run()



# TODOS
# Adjust ray creation to look better --> Set it to 2* BPM!
# tune colors to pitch
# randomly create bodies
# intersect with those bodies
# have those bodies rebroadcast
