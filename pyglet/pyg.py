import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet import clock
import colour
from math import radians, sin, cos
import redis

from body import Body


WIDTH = 1280
HEIGHT = 780

window = pyglet.window.Window(WIDTH, HEIGHT, vsync=False)

redis = redis.StrictRedis(host="localhost", port=6379, password="", decode_responses=True)


class VertexListHolder:
    def __init__(self, vertex_list):
        self.vertex_list = vertex_list

vlh = VertexListHolder(None)

@window.event
def on_draw(*args):
    window.clear()
    msg = redis.get("vertex_list")
    if msg:
        ray_coords_raw, ray_colors_raw = msg.split("|")
        ray_coords = eval(ray_coords_raw) # I solemnly swear I am up to no good
        ray_colors = eval(ray_colors_raw) # I solemnly swear I am up to no good
        if vlh.vertex_list:
            vlh.vertex_list.delete()

        vlh.vertex_list = pyglet.graphics.vertex_list(int(len(ray_coords) / 2),
                        ('v2f', ray_coords),
                        ('c3B', ray_colors))
        vlh.vertex_list.draw(pyglet.gl.GL_LINES)

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

clock.schedule(on_draw)
pyglet.app.run()



# TODOS
# Adjust ray creation to look better --> Set it to 2* BPM!
# tune colors to pitch
# randomly create bodies
# intersect with those bodies
# have those bodies rebroadcast
