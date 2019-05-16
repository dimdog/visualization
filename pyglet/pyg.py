import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet import clock
import colour
from math import radians, sin, cos
import redis
from panel import control_panel
import json

from body import Body


WIDTH = 1280
HEIGHT = 780

window = pyglet.window.Window(WIDTH, HEIGHT)

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
        as_json = json.loads(msg)
        ray_coords = as_json["ray_coords"]
        ray_colors = as_json["ray_colors"]
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
        print('The left mouse button was pressed:{},{}'.format(x,y))

cp_window, cp_window2, cp_gui = control_panel()
clock.schedule(on_draw)
pyglet.app.run()



# TODOS
# Adjust ray creation to look better --> Set it to 2* BPM!
# tune colors to pitch
# randomly create bodies
# intersect with those bodies
# have those bodies rebroadcast
