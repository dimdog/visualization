import colour
import configparser
import pathlib
import random
r = random.Random()

parent_dir = pathlib.Path(__file__).parent.parent.absolute()
config = configparser.ConfigParser()
config.read(parent_dir.joinpath('config.ini'))


redishost = config['DEFAULT']['REDIS_URL']

class Looper(object):

    def __init__(self, graphics, drawer):
        self.graphics = graphics
        self.drawer = drawer

    def poll(self, *args):
        # listen here for the message
        color = colour.Color(hsl=(r.random(),r.random(),r.random()))
        count = r.randint(0,15)
        self.graphics.add_energy_to_system(count, color)
        self.drawer.draw(self.graphics)

if __name__ == "__main__":
    # need to get height and width as args
    from Drawer import Drawer
    from BodyManager import BodyManager, Body
    WIDTH=int(config['DEFAULT']['SCREEN_WIDTH'])
    HEIGHT=int(config['DEFAULT']['SCREEN_HEIGHT'])
    b = Body(WIDTH/2, HEIGHT/2, 100)
    bm = BodyManager(b)
    bm.generate_bodies(15)
    d = Drawer()
    ar = Looper(bm, d)
    d.pyglet_clock.schedule_interval(ar.poll, 0.01)
    d.pyglet.app.run()



