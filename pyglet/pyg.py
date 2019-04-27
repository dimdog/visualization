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

clock.schedule(b.update_vertex_list) # remember this can take a delay
# schedule something that resets the color range every ... ???

@window.event
def on_draw():
    window.clear()
    if b.vertex_list:
        b.vertex_list.draw(pyglet.gl.GL_LINES)

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
