import colour
import configparser
import pathlib
import redis

parent_dir = pathlib.Path(__file__).parent.parent.absolute()
config = configparser.ConfigParser()
config.read(parent_dir.joinpath('config.ini'))


redishost = config['DEFAULT']['REDIS_URL']

class AudioReceiver(object):

    def __init__(self, graphics, drawer):
        self.redis = redis.StrictRedis(host=redishost, port=6379, password="", decode_responses=True)
        self.redis.delete("beat_queue") # clears so we don't have a whole history to fight through
        self.graphics = graphics
        self.drawer = drawer

    def poll(self, *args):
        # listen here for the message
        msg = self.redis.rpop("beat_queue")
        color = None
        count = 0
        if msg is not None:
            if msg.startswith("note:"):
                    note = msg.split("note:")[1]
                    note_sum = (ord(note[0].lower())-97) * 2 # Convert ABCDEFG to a number 0-7
                    if len(note) > 1: # then it is a sharp
                        note_sum+= 1
                    # note_sum is 0-13. We want to get it into the range of 0.0 - 1.0, so...
                    hue = note_sum/13.0
                    random_hue = hue + (r.randint(-self.random_factor, self.random_factor) / 100.0)
                    color = colour.Color(hsl=(random_hue, 1, 0.5))
            elif msg.startswith("noteoctave:"):
                    noteoctave = msg.split("noteoctave:")[1]
                    note, octave = noteoctave.split(",")
                    note_sum = (ord(note[0].lower())-97) * 2 # Convert ABCDEFG to a number 0-7
                    if len(note) > 1: # then it is a sharp
                        note_sum+= 1
                    # note_sum is 0-13
                    noteoctave_sum = octave * note_sum
                    # noteoctave_sum is 0-65. We want to get it into the range of 0.0 - 1.0, so...
                    hue = note_sum/13.0
                    random_hue = hue + (r.randint(-self.random_factor, self.random_factor) / 100.0)
                    color = colour.Color(hsl=(random_hue, 1, 0.5))
            elif not msg.startswith("note:"):
                count = int(msg)
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
    ar = AudioReceiver(bm, d)
    d.pyglet_clock.schedule_interval(ar.poll, 0.01)
    d.pyglet.app.run()



