import configparser
import pathlib
import pyglet
from pyglet import clock
from ray import Ray, scale_color
from AudioReceiver import AudioReceiver
parent_dir = pathlib.Path(__file__).parent.parent.absolute()
config = configparser.ConfigParser()
config.read(parent_dir.joinpath('config.ini'))


WIDTH=int(config['DEFAULT']['SCREEN_WIDTH'])
HEIGHT=int(config['DEFAULT']['SCREEN_HEIGHT'])
window = pyglet.window.Window(WIDTH, HEIGHT)

class Drawer(object):

    def __init__(self):
        self.pyglet_clock = clock
        self.pyglet = pyglet

    @window.event
    def draw(self, bm):
        window.clear()
        ray_coords = []
        ray_colors = []
        for b in [bm.main_body, *bm.bodies]:
            circle_coords = b.circle.get_coords(b.shape)
            circle_colors = b.circle.get_monocolored_arg(scale_color(b.lastColor), int(len(circle_coords[1])/2))
            vl = pyglet.graphics.vertex_list(int(len(circle_coords[1]) / 2),
                                             tuple(circle_coords),
                                             tuple(circle_colors))
            vl.draw(pyglet.gl.GL_POLYGON)

            ray_coords.extend(b.ray_coords)
            ray_colors.extend(b.ray_colors)
        vertex_list = pyglet.graphics.vertex_list(int(len(ray_coords) / 2),
                                                  ('v2f', ray_coords),
                                                  ('c3B', ray_colors))
        vertex_list.draw(pyglet.gl.GL_LINES)


    def loop(self):
        pass
