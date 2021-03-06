import colour
import uuid
import configparser
import pathlib
from math import radians, sin, cos, sqrt
import random
import redis
import json
from ray import Ray, scale_color
from shapes import Shape, Circle
r = random.Random()
parent_dir = pathlib.Path(__file__).parent.parent.absolute()
config = configparser.ConfigParser()
config.read(parent_dir.joinpath('config.ini'))


WIDTH=int(config['DEFAULT']['SCREEN_WIDTH'])
HEIGHT=int(config['DEFAULT']['SCREEN_HEIGHT'])
redishost = config['DEFAULT']['REDIS_URL']

class BodyManager(object):

    def __init__(self, main_body, *bodies):
        self.main_body = main_body
        self.bodies = list(bodies)
        self.redis = redis.StrictRedis(host=redishost, port=6379, password="", decode_responses=True)
        self.redis.delete("beat_queue") # clears so we don't have a whole history to fight through
        self.threshold = 7
        self.counter = 0
        self.MODE = "MFCC+BEAT"
        #self.MODE = "BEAT"
        #self.MODE = "MFCC"
        self.COLOR_MODE = "TONE"
        #self.COLOR_MODE = "RANDOM"
        self.color = None
        self.random_factor = 5
        self.COLLISION_MODE="ALL"
        self.COLLISION_MODE="NOTMAIN"
        self.GRAPHICS_MODE="WEB"
        #self.GRAPHICS_MODE="PYGLET"

    def generate_bodies(self, n):
        """ generates n bodies and adds them to self"""
        not_allowed = [(b.x, b.y, b.radius) for b in [self.main_body, *self.bodies]]
        for i in range(n):
            x,y = self.find_legal_coordinates(50, not_allowed)
            self.bodies.append(Body(x, y, 50, scanning_mode="RANDOM"))

    def find_legal_coordinates(self, radius, not_allowed):
        rx = r.randint(radius,WIDTH-radius)
        ry = r.randint(radius,HEIGHT-radius)

        for circ in not_allowed:
            distance = sqrt((abs(rx - circ[0]) ** 2) + (abs(ry - circ[1]) ** 2))
            if distance <  circ[2] + radius:
                return self.find_legal_coordinates(radius, not_allowed)
        return (rx, ry)

    def get_collision_list(self):
        collision_list = []
        if self.COLLISION_MODE == "ALL":
            collision_list = [self.main_body, *self.bodies]
        elif self.COLLISION_MODE == "NOTMAIN":
            collision_list = self.bodies
        return collision_list

    def gen_vertex_list(self):
        if self.GRAPHICS_MODE == "PYGLET":
            ray_coords = []
            ray_colors = []
            circle_array = []
            for b in [self.main_body, *self.bodies]:
                circle_coords = b.circle.get_coords(b.shape)
                circle_colors = b.circle.get_monocolored_arg(scale_color(b.lastColor), int(len(circle_coords[1])/2))
                circle_array.append({"coords": circle_coords, "colors": circle_colors})
                ray_coords.extend(b.ray_coords)
                ray_colors.extend(b.ray_colors)
            self.redis.lpush("vertex_list", json.dumps({"ray_coords":list(ray_coords),"ray_colors":list(ray_colors), "circles": circle_array}))
        elif self.GRAPHICS_MODE == "WEB":
            circleColors = set()
            lineColors = set()
            circles = []
            rays = []
            for b in [self.main_body, *self.bodies]:
                circleColors.add(b.lastColor.hex_l)
                circles.append({"radius": b.radius, "origin": [b.x-WIDTH/2, b.y-HEIGHT/2, 0], "color": b.lastColor.hex_l, "id": b.uuid})
                for ray in b.rays:
                    if ray.active:
                        lineColors.add(ray.color1.hex_l)
                        rays.append({"p1": [ray.x1-WIDTH/2, ray.y1-HEIGHT/2, 0], "p2": [ray.x2-WIDTH/2, ray.y2-HEIGHT/2, 0], "color": ray.color1.hex_l, "id":ray.uuid})
            self.redis.lpush("geometry", json.dumps({"circleColors": list(circleColors),
                                             "lineColors": list(lineColors),
                                             "circles": circles,
                                             "rays": rays
                                            }))

    def check_ray_collision(self, ray):
        collision_list = self.get_collision_list()
        for b in collision_list:
            distance = sqrt((abs(ray.x2 - b.x) ** 2) + (abs(ray.y2 - b.y) ** 2))
            if distance < b.radius:
                return b
        return None

    def reposition_body(self, body, xystr):
        x, y = xystr.split(",")
        body.x = int(x)
        body.y = int(y)

    def update_vertex_lists(self, *args):
        # listen here for the message
        msg = self.redis.rpop("beat_queue")
        if msg is not None:
            if msg.startswith("gui:"):
                if msg.startswith("gui:bodies:setmain:"):
                    b = self.main_body
                    new_main_index = int(msg.split(":")[-1])
                    new_main = self.bodies.pop(new_main_index)
                    self.bodies.append(b)
                    self.main_body = new_main
                    print(self.main_body)
                    print("changing main body")
                elif msg.startswith("gui:bodies:setlocation:"):
                    body, location = msg.split(":")[-2:]
                    body = int(body)
                    x,y = [int(t) for t in location.split(",")]
                    self.main_body.x = x
                    self.main_body.y = y
                elif msg.startswith("gui:bodies:setlocations:"):
                    locations = msg.split(":")[-1]
                    total_bodies = locations.split("|")
                    if len(total_bodies) != len(self.bodies) +1:
                        print("Invalid bodies message")
                    else:
                        main_bod = total_bodies[0]
                        self.reposition_body(self.main_body, main_bod)
                        for counter,bod in enumerate(total_bodies[1:]):
                            self.reposition_body(self.bodies[counter], bod)
                        print("bodies repositioned!")

            elif self.COLOR_MODE == "TONE" and msg.startswith("note:"):
                    note = msg.split("note:")[1]
                    note_sum = (ord(note[0].lower())-97) * 2 # Convert ABCDEFG to a number 0-7
                    if len(note) > 1: # then it is a sharp
                        note_sum+= 1
                    # note_sum is 0-13. We want to get it into the range of 0.0 - 1.0, so...
                    hue = note_sum/13.0
                    random_hue = hue + (r.randint(-self.random_factor, self.random_factor) / 100.0)
                    self.color = colour.Color(hsl=(random_hue, 1, 0.5))
            elif self.COLOR_MODE == "TONE" and msg.startswith("noteoctave:"):
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
                    self.color = colour.Color(hsl=(random_hue, 1, 0.5))
            elif self.MODE == "MFCC":
                try:
                    count = int(msg)
                    self.counter += count
                    while self.counter >= self.threshold:
                        self.main_body.add_ray(bounce=False, decay=True)
                        self.counter -= self.threshold
                except:
                    pass
            elif self.MODE == "BEAT":
                if msg == "BEAT":
                    self.main_body.add_ray()
                    self.main_body.add_ray()
                    self.main_body.add_ray()
                    self.main_body.add_ray()
                    self.main_body.add_ray()
            elif self.MODE == "MFCC+BEAT":
                if msg == "Beat":
                    while self.counter >= self.threshold:
                        self.main_body.add_ray(color=self.color)
                        self.counter -= self.threshold
                elif not msg.startswith("note:"):
                    count = int(msg)
                    self.counter += count

        for b in [self.main_body, *self.bodies]:
            b.update_vertex_list()
            for ray in b.rays:
                # I know this sucks - so we iterate through all bodies to go through all the rays in all the bodies, and compare them to all the bodies - fuck!
                hit_body = self.check_ray_collision(ray)
                if hit_body:
                    # "absorb" a "tick" of the ray TODO
                    ray.active = False # temporary solution
                    hit_body.add_energy(ray.magnitude, ray.color1, ray.color2) # another temp solution
        self.gen_vertex_list()

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
    #b = Body(WIDTH, HEIGHT/2, 100, scanning_min = 110, scanning_max=250)
    b = Body(WIDTH/2, HEIGHT/2, 100)
    #b2 = Body(WIDTH/4, HEIGHT/4, 50, scanning_mode="RANDOM")
    #b3 = Body(WIDTH/4+WIDTH/2, HEIGHT/4, 50, scanning_mode="RANDOM")
    #b4 = Body(WIDTH/4, HEIGHT/4+HEIGHT/2, 50, scanning_mode="RANDOM")
    #b5 = Body(WIDTH/4+WIDTH/2, HEIGHT/4+HEIGHT/2, 50, scanning_mode="RANDOM")
    #bm = BodyManager(b, b2, b3, b4, b5)
    bm = BodyManager(b)
    bm.generate_bodies(15)
    while True:
        bm.update_vertex_lists()


