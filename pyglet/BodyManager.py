import colour
import uuid
import configparser
import pathlib
from math import radians, sin, cos, sqrt
import random
import json
from ray import Ray, scale_color
from shapes import Shape, Circle
import pyglet
from pyglet import clock
r = random.Random()
parent_dir = pathlib.Path(__file__).parent.parent.absolute()
config = configparser.ConfigParser()
config.read(parent_dir.joinpath('config.ini'))
WIDTH=int(config['DEFAULT']['SCREEN_WIDTH'])
HEIGHT=int(config['DEFAULT']['SCREEN_HEIGHT'])


class BodyManager(object):

    def __init__(self, main_body, *bodies):
        self.main_body = main_body
        self.bodies = list(bodies)
        self.threshold = 7
        self.counter = 0
        self.MODE = "MFCC+BEAT"
        self.color = None
        self.random_factor = 5
        self.COLLISION_MODE="ALL"
        self.COLLISION_MODE="NOTMAIN"

    def generate_bodies(self, n):
        """ generates n bodies and adds them to self"""
        not_allowed = [(b.x, b.y, b.radius) for b in [self.main_body, *self.bodies]]
        for i in range(n):
            x,y = self.find_legal_coordinates(20, not_allowed)
            self.bodies.append(Body(x, y, 20, scanning_mode="RANDOM"))

    def find_legal_coordinates(self, radius, not_allowed):
        buff = 20
        rx = r.randint(radius+buff,WIDTH-(radius+buff))
        ry = r.randint(radius+buff,HEIGHT-(radius+buff))

        for circ in not_allowed:
            distance = sqrt((abs(rx - circ[0]) ** 2) + (abs(ry - circ[1]) ** 2))
            if distance <  circ[2] + radius+buff:
                return self.find_legal_coordinates(radius, not_allowed)
        return (rx, ry)

    def get_collision_list(self):
        collision_list = []
        if self.COLLISION_MODE == "ALL":
            collision_list = [self.main_body, *self.bodies]
        elif self.COLLISION_MODE == "NOTMAIN":
            collision_list = self.bodies
        return collision_list

    def check_ray_collision(self, ray):
        collision_list = self.get_collision_list()
        for b in collision_list:
            distance = sqrt((abs(ray.x2 - b.x) ** 2) + (abs(ray.y2 - b.y) ** 2))
            if distance < b.radius:
                return b
        return None

    def add_energy_to_system(self, amount, color):
        self.counter += amount
        self.color = color if color else self.color
        while self.counter >= self.threshold:
            self.main_body.add_ray(color=self.color)
            self.counter -= self.threshold
        self.update_vertex_lists()

    def update_vertex_lists(self, *args):
        for b in [self.main_body, *self.bodies]:
            b.update_vertex_list()
            for ray in b.rays:
                # I know this sucks - so we iterate through all bodies to go through all the rays in all the bodies, and compare them to all the bodies - fuck!
                hit_body = self.check_ray_collision(ray)
                if hit_body:
                    # "absorb" a "tick" of the ray TODO
                    ray.active = False # temporary solution
                    hit_body.add_energy(ray.magnitude, ray.color1, ray.color2) # another temp solution

class Body(object):

    MAX_MAGNITUDE = 500
    MIN_MAGNITUDE = 100

    def __init__(self, x, y, radius, degree=150, scanning_max = 360, scanning_min = 0, scanning_mode="CIRCLE", origin="PERIMETER"):
        #TODO origin = CENTER is broken for rebroadcasting
        self.uuid = str(uuid.uuid4())
        self.x = x
        self.y = y
        self.radius = radius
        # for drawing
        self.colorDict = dict()
        self.lastColor = colour.Color("Blue")
        self.shape = Shape(center=(self.x,self.y))
        self.circle = Circle(self.radius*2)
        # end drawing section
        self.rays = []
        self.vertex_list = None
        r_b = [color for color in colour.Color("Red").range_to(colour.Color("Green"), 120)]
        b_g = [color for color in colour.Color("Green").range_to(colour.Color("Blue"), 120)]
        g_r = [color for color in colour.Color("Blue").range_to(colour.Color("Red"), 120)]
        self.colors =  r_b+b_g+g_r
        self.energy = 0
        self.energy_color = None
        self.scanning_max = scanning_max
        self.scanning_min = scanning_min
        if degree > self.scanning_max:
            degree = self.scanning_max
        elif degree < self.scanning_min:
            degree = self.scanning_min
        self.degree = degree
        self.scanning_mode = scanning_mode
        #self.scanning_mode_options = ["CIRCLE", "RANDOM"]
        self.origin = origin
        #self.origin_modes = ["CENTER", "PERIMETER"]

    def __repr__(self):
        return "<Body x={} y={} radius={}>".format(self.x, self.y, self.radius)

    def get_color(self):
        return self.colors[int(self.degree)]

    def add_energy(self, magnitude, color1, color2=None):
        # ignore color 2 for now :shrug:
        if not self.energy_color:
            self.energy_color = color1
        else:
            # average them
            current_hue = self.energy_color.get_hue()
            new_hue = color1.get_hue()
            average_hue = ((current_hue * self.energy) + (new_hue * magnitude))/(self.energy + magnitude)
            self.energy_color.set_hue(average_hue)
        self.energy += magnitude * 3



    def add_ray(self, degree=None, color=None, magnitude=None, bounce=False, decay=False):
        if degree:
            self.degree = degree
        if not color:
            color = self.get_color()
        else:
            color = colour.Color(color) # else its just a reference and can change!
        self.colorDict[self.degree] = color
        self.lastColor = color
        if not magnitude:
            magnitude = r.randint(self.MIN_MAGNITUDE, self.MAX_MAGNITUDE)
        if self.origin=="PERIMETER":
            x_point = self.radius * cos(radians(self.degree)) + self.x
            y_point = self.radius * sin(radians(self.degree)) + self.y
            self.rays.append(Ray(x_point, y_point, self.degree, magnitude, color, bounce=bounce, decay=decay))
        else:
            self.rays.append(Ray(self.x, self.y, self.degree, magnitude, color, bounce=bounce, decay=decay))
        if self.scanning_mode == "CIRCLE":
            self.degree = self.degree + 1
            if self.degree >= self.scanning_max:
                self.degree = self.scanning_min
        elif self.scanning_mode == "RANDOM":
            self.degree = r.randrange(self.scanning_min, self.scanning_max)

    def get_vertices_and_colors(self):
        rays = [ray for ray in self.rays] # snapshot

        rays_c = [ray.get_coordinates() for ray in rays]
        colors = [ray.get_colors() for ray in rays]
        ray_coords = []
        [ray_coords.extend(ray) for ray in rays_c]
        ray_colors = []
        [ray_colors.extend(color) for color in colors]
        return ray_coords, ray_colors

    def expend_energy(self):
        if self.energy > self.MIN_MAGNITUDE:
            magnitude = r.randint(self.MIN_MAGNITUDE, self.MAX_MAGNITUDE/2)
            if magnitude > self.energy:
                magnitude = self.energy
            self.energy -= magnitude
            # TODO make a range +/- 10 hue on the current energy color and randomly pick from it
            self.add_ray(color=self.energy_color, magnitude=magnitude, bounce=True, decay=True)

    def update_vertex_list(self, *args):
        self.expend_energy()
        remove = []
        for ray in self.rays:
            if not ray.active:
                remove.append(ray)
            else:
                ray.update()
        for ray in remove:
            self.rays.remove(ray)
        ray_coords, ray_colors = self.get_vertices_and_colors()
        self.ray_coords = ray_coords
        self.ray_colors = ray_colors

if __name__ == "__main__":
    # need to get height and width as args
    b = Body(WIDTH/2, HEIGHT/2, 100)
    bm = BodyManager(b)
    bm.generate_bodies(15)
    ar = AudioReceiver(bm)
    clock.schedule_interval(ar.poll, 0.01)
    pyglet.app.run()



