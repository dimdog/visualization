import colour
from math import radians, sin, cos
import random
r = random.Random()
from ray import Ray
# !!!! TODO
import pyglet
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
        # TODO REMOVE
        self.vertex_list = pyglet.graphics.vertex_list(int(len(ray_coords) / 2),
                        ('v2f', ray_coords),
                        ('c3B', ray_colors))
