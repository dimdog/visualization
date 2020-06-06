import pyglet
import configparser
from pyglet.window import key
from pyglet.window import mouse
from pyglet import clock
import colour
from math import radians, sin, cos
import redis
from panel import control_panel
import json

config = configparser.ConfigParser()
config.read('config.ini')

WIDTH=int(config['DEFAULT']['SCREEN_WIDTH'])
HEIGHT=int(config['DEFAULT']['SCREEN_HEIGHT'])
#redishost = "10.0.1.18"
redishost = config['DEFAULT']['REDIS_URL']

window = pyglet.window.Window(WIDTH, HEIGHT)

redis = redis.StrictRedis(host=redishost, port=6379, password="", decode_responses=True)


@window.event
def on_draw(*args):
    window.clear()
    msg = redis.get("vertex_list")
    if msg:
        as_json = json.loads(msg)
        ray_coords = as_json.get("ray_coords", [])
        ray_colors = as_json.get("ray_colors", [])
        circles = as_json.get("circles", [])
        if not ray_coords:
            ray_coords = []
            ray_colors = []
        vertex_list = pyglet.graphics.vertex_list(int(len(ray_coords) / 2),
                        ('v2f', ray_coords),
                        ('c3B', ray_colors))
        vertex_list.draw(pyglet.gl.GL_LINES)
        for circle in circles:
            vl = pyglet.graphics.vertex_list(int(len(circle['coords'][1])/2),
                    tuple(circle['coords']),
                    tuple(circle['colors']))
            vl.draw(pyglet.gl.GL_POLYGON)


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

#cp_window, cp_window2, cp_gui = control_panel()
clock.schedule_interval(on_draw, 0.01)
pyglet.app.run()



# TODOS
# Adjust ray creation to look better --> Set it to 2* BPM!
# tune colors to pitch
# randomly create bodies
# intersect with those bodies
# have those bodies rebroadcast
