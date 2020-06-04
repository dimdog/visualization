import random
from math import radians, sin, cos, sqrt
r = random.Random()
WIDTH=1280
HEIGHT=800
CEILING=0

def scale_color(color):
    rgb_color = color.get_rgb()
    return tuple(int(elem * 255) for elem in rgb_color)

class Ray(object):
    BOUNCE=False
    decay_rate=-.001
    growth_rate=.5

    def __init__(self, x, y, angle, magnitude, color1, color2=None, bounce=False, decay=False):
        # Colors are expected to colour objects
        #debug
        self.marked = True if r.random() > .99 else False
        self.name = str(r.random()*1000)[:4]
        # TODO turn this thing into something that calculates the next "step" based on slope and stepping, instead of pushing the slope...
        self.decay = decay
        self.bounce = bounce
        self.x1 = x
        self.y1 = y
        self.angle = angle
        self.x_slope = cos(radians(self.angle))
        self.y_slope = sin(radians(self.angle))
        self.x2 = self.x1 + self.x_slope
        self.y2 = self.y1 + self.y_slope
        self.magnitude = magnitude
        self.color1 = color1
        self.color2 = color2 or color1
        self.active = True

    def __repr__(self):
        return "name:{} ({},{}), ({},{})".format(self.name, self.x1, self.y1, self.x2, self.y2)

    def get_coordinates(self):
        return [self.x1, self.y1, self.x2, self.y2]

    def get_colors(self):
        return (*scale_color(self.color1), *scale_color(self.color2))

    def move_ray(self):
        # why *2?
        self.x2+= self.x_slope*2
        self.y2+= self.y_slope*2
        self.x1+= self.x_slope*2
        self.y1+= self.y_slope*2

    def enforce_bounds(self):
        if self.x2 < 0:
            self.x2 = 0
            self.y2-=self.y_slope
            return True
        elif self.x2 > WIDTH:
            self.x2 = WIDTH
            self.y2-=self.y_slope
            return True
        if self.y2 < CEILING:
            self.y2 = CEILING
            self.x2-=self.x_slope
            return True
        elif self.y2 > HEIGHT:
            self.y2 = HEIGHT
            self.x2-=self.x_slope
            return True
        return False

    def resize(self):
        current_magnitude = sqrt((abs(self.x2 - self.x1) ** 2) + (abs(self.y2 - self.y1) ** 2))
        change_rate = self.growth_rate
        if current_magnitude == self.magnitude:
            return
        if current_magnitude > self.magnitude:
            change_rate = self.decay_rate
        new_magnitude = min(self.magnitude, current_magnitude + (current_magnitude * change_rate))
        rand_factor = r.random() / 2
        self.x2 = self.x2 + self.x_slope * change_rate * rand_factor
        self.y2 = self.y2 + self.y_slope * change_rate * rand_factor

    def decay_ray(self):

        self.magnitude = self.magnitude + (self.magnitude * self.decay_rate)
        if self.magnitude < 1:
            self.active = False
            return False
        return True

    def bounce_ray(self):
        # this assumes bounds have already been enforced
        current_magnitude = sqrt((abs(self.x2 - self.x1) ** 2) + (abs(self.y2 - self.y1) ** 2))
        if current_magnitude < 0.5:
            if self.BOUNCE and self.bounce: # global rule, then ray specific rule
                if self.x2 == WIDTH or self.x2 == 0:
                    #flip x growth rate
                    # OLD LOGIC PULL ME OUT
                    self.x_slope = -self.x_slope
                elif self.y2 == HEIGHT or self.y2 == CEILING:
                    #flip y growth rate
                    # OLD LOGIC PULL ME OUT
                    self.y_slope = -self.y_slope
            else:
                self.active = False


    def update(self):
        # decay
        if not self.decay_ray():
            return
        # move
        self.move_ray()
        # bounds check
        if not self.enforce_bounds():
            # grow / shrink / (TODO)collide
            self.resize()
        else:
            # bounce
            self.bounce_ray()

