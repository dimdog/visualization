import colour
from math import radians, sin, cos
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

    def gen_vertex_list(self):
        ray_coords = []
        ray_colors = []
        for b in [self.main_body, *self.bodies]:
            ray_coords.extend(b.ray_coords)
            ray_colors.extend(b.ray_colors)

        self.redis.set("vertex_list", "{}|{}".format(ray_coords, ray_colors))

    def update_vertex_lists(self, *args):
        # listen here for the message
        msg = self.redis.rpop("beat_queue")
        while msg:
            self.main_body.add_ray()
            msg = self.redis.rpop("beat_queue")
        for b in [self.main_body, *self.bodies]:
            b.update_vertex_list()
        self.gen_vertex_list()

class Body(object):

    def __init__(self, x, y, radius, degree=0):
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

    def get_color(self):
        return self.colors[int(self.degree)]

    def add_ray(self, degree=None, color=None):
        if degree:
            self.degree = degree
        if not color:
            color = self.get_color()
        color = self.get_color()
        x_slope = (self.radius * cos(radians(self.degree)))/60
        y_slope = (self.radius * sin(radians(self.degree)))/60
        x_point = self.radius * cos(radians(self.degree)) + self.x
        y_point = self.radius * sin(radians(self.degree)) + self.y
        amplitude = r.randint(10, 100)
        self.rays.append(Ray(x_point, y_point, x_point + x_slope, y_point + y_slope, amplitude, color))
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


    def update_vertex_list(self, *args):
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
    b = Body(WIDTH/2, HEIGHT/2, 20)
    bm = BodyManager(b)
    while True:
        bm.update_vertex_lists()


