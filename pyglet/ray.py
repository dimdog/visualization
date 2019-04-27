
def scale_color(color):
    rgb_color = color.get_rgb()
    return tuple(int(elem * 255) for elem in rgb_color)

class Ray(object):

    def __init__(self, x1, y1, x2, y2, amplitude, color1, color2=None):
        # Colors are expected to colour objects
        self.active = True
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.amplitude = amplitude
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
        self.x2 = self.x2 + self.x_slope
        self.y2 = self.y2 + self.y_slope
        if self.counter == self.amplitude:
            self.x1 = self.x1 + self.x_slope
            self.y1 = self.y1 + self.y_slope

        # check for collisions
        # check distance of (x2, y2) from the center of every body, if distance is < radius its a hit
        # MOVE ELSEWHERE TODO
        #if not 0 < self.x2 <= WIDTH or not 0 < self.y2 <= HEIGHT:
        if not 0 < self.x2 <= 1280 or not 0 < self.y2 <= 720:
            self.active = False
        self.counter+=1
        self.counter = min(self.amplitude, self.counter)
