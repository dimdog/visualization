import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet import clock
import pyaudio
import aubio
import colour
from math import radians, sin, cos
import numpy as np



class AudioProcessor(object):
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    hop_s = CHUNK // 2  # hop size


    def __init__(self, source_body):
        self.p = pyaudio.PyAudio()
        self.source_body = source_body
        stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        output=True,
                        input_device_index = self.get_input_device_index(),
                        output_device_index = self.get_output_device_index(),
                        frames_per_buffer = self.CHUNK,
                        stream_callback=self.callback)

        self.a_tempo = aubio.tempo("default", self.CHUNK, self.hop_s, self.RATE)
        self.a_pitch = aubio.pitch("default", self.CHUNK, self.hop_s, self.RATE)
        self.tolerance = 0.8
        self.a_pitch.set_tolerance(self.tolerance)
        self.highest_pitch = 0
        self.lowest_pitch = 99999999
        self.average_pitch = 0
        self.average_pitch_samples = 0
        self.last_average = 0
        stream.start_stream()

    def reset(self):
        self.highest_pitch = 0
        self.lowest_pitch = 99999999
        self.average_pitch = 0
        self.average_pitch_samples = 0

    def get_input_device_index(self):
        for i in range(self.p.get_device_count()):
            if self.p.get_device_info_by_index(i)['name'] == 'Soundflower (2ch)':
                print("Found!{}".format(self.p.get_device_info_by_index(i)['name']))
                return i

    def get_output_device_index(self):
        for i in range(self.p.get_device_count()):
            if self.p.get_device_info_by_index(i)['name'] == 'Built-in Output':
                print("Found!{}".format(self.p.get_device_info_by_index(i)['name']))
                return i

    def callback(self, in_data, frame_count, time_info, status):
        # dir of a_tempo: ['__call__', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'buf_size', 'get_bpm', 'get_confidence', 'get_delay', 'get_delay_ms', 'get_delay_s', 'get_last', 'get_last_ms', 'get_last_s', 'get_last_tatum', 'get_period', 'get_period_s', 'get_silence', 'get_threshold', 'hop_size', 'method', 'samplerate', 'set_delay', 'set_delay_ms', 'set_delay_s', 'set_silence', 'set_tatum_signature', 'set_threshold']
        # pitch is typically in the 0 - 20k range
        ret = np.fromstring(in_data, dtype=np.float32)
        ret = ret[0:self.hop_s]
        pitch = self.a_pitch(ret)[0]
        if pitch > 0 and self.a_pitch.get_confidence() > 0:
            self.average_pitch+=pitch
            self.average_pitch_samples+=1
        is_beat = self.a_tempo(ret)
        if is_beat:
            #print(self.a_tempo.get_bpm())
            self.source_body.add_ray()
            if self.average_pitch_samples > 0:
                average_pitch = self.average_pitch / self.average_pitch_samples
                self.last_average = average_pitch
                self.highest_pitch = max([self.highest_pitch, average_pitch])
                self.lowest_pitch = min([self.lowest_pitch, average_pitch])
                #print("average Pitch:{} highest Pitch:{} lowest Pitch:{}".format(average_pitch, self.highest_pitch, self.lowest_pitch))
                self.average_pitch_samples = 0
                self.average_pitch = 0
            else:
                pass
                #print("last Pitch:{} highest Pitch:{} lowest Pitch:{}".format(self.last_average, self.highest_pitch, self.lowest_pitch))
        return (in_data, pyaudio.paContinue)


class Body(object):

    def __init__(self, x, y, radius, degree=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.degree = degree
        self.rays = {}
        self.vertex_list = None

    def add_ray(self, degree=None):
        if degree:
            self.degree = degree
        if self.degree in self.rays:
            if self.rays[self.degree].active:
                return
            else:
                self.rays.pop(degree)
        color = None # TODO COLOR
        color = colour.Color("Blue")
        x_slope = (self.radius * cos(radians(self.degree)))/3
        y_slope = (self.radius * sin(radians(self.degree)))/3
        x_point = self.radius * cos(radians(self.degree)) + self.x
        y_point = self.radius * sin(radians(self.degree)) + self.y
        self.rays[self.degree] = Ray(x_point, y_point, x_point + x_slope, y_point + y_slope, color)
        self.degree = self.degree + 5

    def get_vertices(self):
        rays = [ray.get_coordinates() for ray in self.rays.values()]
        ray_coords = []
        [ray_coords.extend(ray) for ray in rays]
        return ray_coords

    def get_colors(self):
        rays = [ray.get_coordinates() for ray in self.rays.values()]
        colors = [ray.get_colors() for ray in self.rays.values()]
        ray_colors = []
        [ray_colors.extend(color) for color in colors]
        return ray_colors

    def update_vertex_list(self, *args):
        [ray.update() for ray in self.rays.values()]
        ray_coords = self.get_vertices()
        ray_colors = self.get_colors()
        self.vertex_list = pyglet.graphics.vertex_list(int(len(ray_coords) / 2),
                        ('v2f', ray_coords),
                        ('c3B', ray_colors))


def scale_color(color):
    rgb_color = color.get_rgb()
    return tuple(int(elem * 255) for elem in rgb_color)
    
class Ray(object):

    def __init__(self, x1, y1, x2, y2, color1, color2=None):
        # Colors are expected to colour objects ig...
        self.active = True # TODO
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x_slope = x2-x1
        self.y_slope = y2-y1
        self.color1 = color1
        self.color2 = color2 or color1

    def get_coordinates(self):
        return [self.x1, self.y1, self.x2, self.y2]

    def get_colors(self):
        return (*scale_color(self.color1), *scale_color(self.color2))


    def update(self):
        self.x2 = self.x2 + self.x_slope
        self.y2 = self.y2 + self.y_slope
        # need termination logic


vertex_list = pyglet.graphics.vertex_list(2,
    ('v2f', (10, 15, 30, 35)),
    ('c3B', (0, 0, 255, 0, 255, 0))
)
vertex_list2 = pyglet.graphics.vertex_list(2,
    ('v2f', (10.0, 40.0, 30.0, 60.0)),
    ('c3B', (0, 0, 255, 0, 255, 0))
)


window = pyglet.window.Window(vsync=0)
b = Body(200, 200, 20)
a = AudioProcessor(b)

clock.schedule(b.update_vertex_list)

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
