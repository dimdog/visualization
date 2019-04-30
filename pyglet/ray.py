from math import sqrt

def scale_color(color):
    rgb_color = color.get_rgb()
    return tuple(int(elem * 255) for elem in rgb_color)

class Ray(object):
    decay_rate = 0.01 # percentage decay rate

    def __init__(self, x1, y1, x2, y2, magnitude, color1, color2=None, bounce=False, decay=False):
        # Colors are expected to colour objects
        # TODO turn this thing into something that calculates the next "step" based on slope and stepping, instead of pushing the slope...
        self.decay = decay
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
        self.color1 = color1
        self.color2 = color2 or color1

    def get_coordinates(self):
        return [self.x1, self.y1, self.x2, self.y2]

    def get_colors(self):
        return (*scale_color(self.color1), *scale_color(self.color2))


    def update(self):
        #decay is busted
        if self.decay:
            pass

        self.x2 = self.x2 + self.x_slope
        self.y2 = self.y2 + self.y_slope
        current_magnitude = sqrt((abs(self.x2 - self.x1) ** 2) + (abs(self.y2 - self.y1) ** 2))
        if current_magnitude >= self.magnitude:
            self.x1 = self.x1 + self.x_slope
            self.y1 = self.y1 + self.y_slope

        # TODO implement bounce (negate slope when we hit the wall...but i'd love to have it sink into / grow out of the wall
        #if not 0 < self.x2 <= WIDTH or not 0 < self.y2 <= HEIGHT:
        if not 0 < self.x2 <= 1280 or not 0 < self.y2 <= 720:
            self.active = False
