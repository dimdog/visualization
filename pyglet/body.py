import colour
from math import radians, sin, cos, sqrt
import random
r = random.Random()
from ray import Ray
import redis

class BodyManager(object):

    def __init__(self, main_body, *bodies):
        self.main_body = main_body
        self.bodies = bodies
        self.redis = redis.StrictRedis(host="localhost", port=6379, password="", decode_responses=True)
        self.redis.delete("beat_queue") # clears so we don't have a whole history to fight through
        self.threshold = 7
        self.counter = 0
        self.color = None
        self.random_factor = 5
        self.MODE = "MFCC+BEAT"
        self.COLOR_MODE = "TONE"
        #self.COLOR_MODE = "RANDOM"
        #self.MODE = "BEAT"
        #self.MODE = "MFCC"

    def gen_vertex_list(self):
        ray_coords = []
        ray_colors = []
        for b in [self.main_body, *self.bodies]:
            ray_coords.extend(b.ray_coords)
            ray_colors.extend(b.ray_colors)

        self.redis.set("vertex_list", "{}|{}".format(ray_coords, ray_colors))

    def check_ray_collision(self, ray):
        for b in [self.main_body, *self.bodies]:
            distance = sqrt((abs(ray.x2 - b.x) ** 2) + (abs(ray.y2 - b.y) ** 2))
            if distance < b.radius:
                return b
        return None


    def update_vertex_lists(self, *args):
        # listen here for the message
        msg = self.redis.rpop("beat_queue")
        while msg:
            if self.COLOR_MODE == "TONE" and msg.startswith("note:"):
                    note = msg.split("note:")[1]
                    note_sum = (ord(note[0].lower())-97) * 2
                    if len(note) > 1: # then it is a sharp
                        note_sum+= 1
                    # note_sum is 0-13. We want to get it into the range of 0.0 - 1.0, so...
                    hue = note_sum/13.0
                    random_hue = hue + (random.randint(-self.random_factor, self.random_factor) / 100.0)
                    self.color = colour.Color(hsl=(random_hue, 1, 0.5))
            elif self.MODE == "MFCC":
                try:
                    count = int(msg)
                    self.counter += count
                    while self.counter >= self.threshold:
                        self.main_body.add_ray()
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
                else:
                    count = int(msg)
                    self.counter += count
            msg = self.redis.rpop("beat_queue")

        for b in [self.main_body, *self.bodies]:
            b.update_vertex_list()
            for ray in b.rays:
                # I know this sucks - so we iterate through all bodies to go through all the rays in all the bodies, and compare them to all the bodies - fuck!
                hit_body = self.check_ray_collision(ray)
                if hit_body:
                    # "absorb" a "tick" of the ray TODO
                    ray.active = False # temporary solution
                    magnitude = sqrt((abs(ray.x2 - ray.x1) ** 2) + (abs(ray.y2 - ray.y1) ** 2))
                    hit_body.add_energy(magnitude, ray.color1, ray.color2) # another temp solution
        self.gen_vertex_list()

class Body(object):

    MAX_MAGNITUDE = 100
    MIN_MAGNITUDE = 10

    def __init__(self, x, y, radius, degree=150):
        self.x = x
        self.y = y
        self.radius = radius
        self.degree = degree
        self.rays = []
        self.vertex_list = None
        r_b = [color for color in colour.Color("Red").range_to(colour.Color("Green"), 120)]
        b_g = [color for color in colour.Color("Green").range_to(colour.Color("Blue"), 120)]
        g_r = [color for color in colour.Color("Blue").range_to(colour.Color("Red"), 120)]
        self.colors =  r_b+b_g+g_r
        self.energy = 0
        self.energy_color = None

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
        x_slope = (self.radius * cos(radians(self.degree)))/60
        y_slope = (self.radius * sin(radians(self.degree)))/60
        x_point = self.radius * cos(radians(self.degree)) + self.x
        y_point = self.radius * sin(radians(self.degree)) + self.y
        if not magnitude:
            magnitude = r.randint(self.MIN_MAGNITUDE, self.MAX_MAGNITUDE)
        self.rays.append(Ray(x_point, y_point, x_point + x_slope, y_point + y_slope, magnitude, color, bounce=bounce, decay=decay))
        self.degree = self.degree + 1
        if self.degree == 360:
            self.degree = 0

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
    WIDTH=1280
    HEIGHT=720
    b = Body(WIDTH/2, HEIGHT/2, 50)
    b2 = Body(WIDTH/4, HEIGHT/4, 50)
    b3 = Body(WIDTH/4+WIDTH/2, HEIGHT/4, 50)
    b4 = Body(WIDTH/4, HEIGHT/4+HEIGHT/2, 50)
    b5 = Body(WIDTH/4+WIDTH/2, HEIGHT/4+HEIGHT/2, 50)
    bm = BodyManager(b, b2, b3, b4, b5)
    while True:
        bm.update_vertex_lists()


