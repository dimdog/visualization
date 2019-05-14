from math import sqrt
import random
r = random.Random()
WIDTH=1280
HEIGHT=720

def scale_color(color):
    rgb_color = color.get_rgb()
    return tuple(int(elem * 255) for elem in rgb_color)

class Ray(object):
    BOUNCE=True
    GRACE_PERIOD_LENGTH = 7

    def __init__(self, x1, y1, x2, y2, magnitude, color1, color2=None, bounce=False, decay=False):
        # Colors are expected to colour objects
        # TODO turn this thing into something that calculates the next "step" based on slope and stepping, instead of pushing the slope...
        self.decay = decay
        self.decaying = False
        self.bounce = bounce
        self.active = True
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.magnitude = magnitude
        self.counter = 0
        self.x_slope = x2-x1
        self.y_slope = y2-y1
        self.new_x_slope = None
        self.new_y_slope = None
        self.color1 = color1
        self.color2 = color2 or color1
        self.marked = True if r.random() > .99 else False
        self.name = str(r.random()*1000)[:4]
        self.absorbing = False
        self.bouncing = False
        #debug
        self.has_bounced=False
        self.grace_period = 0

    def __repr__(self):
        return "name:{} ({},{}), ({},{})".format(self.name, self.x1, self.y1, self.x2, self.y2)

    def get_coordinates(self):
        return [self.x1, self.y1, self.x2, self.y2]

    def get_colors(self):
        return (*scale_color(self.color1), *scale_color(self.color2))


    def update(self):

        if not self.absorbing and not self.bouncing:
            self.x2 = self.x2 + self.x_slope
            self.y2 = self.y2 + self.y_slope
        self.x1 = self.x1 + self.x_slope
        self.y1 = self.y1 + self.y_slope
        current_magnitude = sqrt((abs(self.x2 - self.x1) ** 2) + (abs(self.y2 - self.y1) ** 2))
        if self.bouncing:
            if current_magnitude < 1:
                self.decaying = False
                self.bouncing = False
                self.x2 = self.x1
                self.y2 = self.y1
                self.x_slope = self.new_x_slope
                self.y_slope = self.new_y_slope
        elif self.decaying:
            rand_factor = r.random() / 2
            self.x2 = self.x2 - self.x_slope * rand_factor
            self.y2 = self.y2 - self.y_slope * rand_factor
            current_magnitude = sqrt((abs(self.x2 - self.x1) ** 2) + (abs(self.y2 - self.y1) ** 2))
            self.magnitude = current_magnitude
        elif current_magnitude <= self.magnitude:
            rand_factor = r.random()
            self.x2 = self.x2 + self.x_slope * rand_factor
            self.y2 = self.y2 + self.y_slope * rand_factor
            rand_factor = r.random() / 3
            self.x1 = self.x1 + self.x_slope * rand_factor
            self.y1 = self.y1 + self.y_slope * rand_factor
        elif current_magnitude  >= self.magnitude and self.decay:
            self.decaying = True

        if self.decaying and current_magnitude < 1 and not self.bouncing:
            self.active = False
        if self.has_bounced and not self.bouncing:
            self.grace_period-=1

        if (not 0 < self.x2 <= WIDTH or not 0 < self.y2 <= HEIGHT) and not self.bouncing and self.grace_period <= 0:
            if self.BOUNCE and self.bounce: # global rule, then ray specific rule
                self.grace_period = self.GRACE_PERIOD_LENGTH
                self.has_bounced = True
                self.bouncing = True
                if not 0 < self.x2 <= WIDTH:
                    self.new_x_slope = - self.x_slope
                else:
                    self.new_x_slope = self.x_slope
                if not 0 < self.y2 <= HEIGHT:
                    self.new_y_slope = - self.y_slope
                else:
                    self.new_y_slope = self.y_slope
            else:
                self.active = False
