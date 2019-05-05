import pyglet
import glooey
import redis
redis = redis.StrictRedis(host="localhost", port=6379, password="", decode_responses=True)

class Circle(glooey.Button):
    custom_size_hint = 50, 50

    class Base(glooey.Background):
        custom_color = '#ffffff'

    def __init__(self, number, main=False):
        text = str(number)
        super().__init__(text)
        self.set_image(pyglet.resource.image('circle50.png'))
        self.number = number
        self.managers = []
        self.main = main
        self.cc = '#204a87'

    def add_manager(self, manager):
        self.managers.append(manager)

    def on_click(self, widget):
        self.cc = '#204a87'
        for manager in self.managers:
            manager.selected = self

    def reposition(self, x, y):
        self.text = "{}:M".format(self.number) if self.main else "{}".format(self.number)
        self.custom_color = self.cc
        self._resize(glooey.Rect(x,y,50,50))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.reposition(x-30,y-30)

class TogglePerformer(glooey.Button):
    custom_size_hint = 200, 100

    class Base(glooey.Background):
        custom_color = '#204a87'

    def __init__(self, text, circles=None):
        super().__init__(text)
        self.circles = circles
        [c.add_manager(self) for c in self.circles]
        self.selected = None


    def on_click(self, widget):
        if self.circles:
            print(self.selected.number)
            for c in self.circles:
                if c == self.selected:
                    c.main = True
                else:
                    c.main = False
                    c.cc = '#204a87'
            redis.lpush("beat_queue", "gui:bodies:setmain:{}".format(self.selected.number))
            #TODO send to redis

class SaveLocations(glooey.Button):
    custom_size_hint = 200, 100

    class Base(glooey.Background):
        custom_color = '#204a87'

    def __init__(self, text, circles=None):
        super().__init__(text)
        self.circles = circles
        [c.add_manager(self) for c in self.circles]

    def on_mouse_press(self, *args):
        print("clicked")
        if self.circles:
            #self.text = "x:{} y:{}".format(self.selected.rect.left, self.selected.rect.bottom)
            #redis.lpush("beat_queue", "gui:bodies:setlocation:{}:{},{}".format(self.selected.number, round(self.selected.rect.left)*4, round(self.selected.rect.bottom)*4))
            # send locations of circles to redis
            msg_list = []
            for c in self.circles:
                msg_list.append((round(c.rect.left*4), round(c.rect.bottom*4)))
            msg = "|".join(["{},{}".format(a[0], a[1]) for a in msg_list])
            print(msg)
            redis.lpush("beat_queue", "gui:bodies:setlocations:{}".format(msg))




def control_panel():

    WIDTH = 800
    HEIGHT = 1000

    window = pyglet.window.Window(WIDTH, HEIGHT)
    gui = glooey.Gui(window)
    grid = glooey.Grid(2,2)

    G_WIDTH = 1280/4
    G_HEIGHT = 780/4
    window2 = pyglet.window.Window(G_WIDTH+100, G_HEIGHT)
    gui2 = glooey.Gui(window2)
    def make_initial_circles():
        c0 = Circle(0, main=True)
        c1 = Circle(1)
        c2 = Circle(2)
        c3 = Circle(3)
        c4 = Circle(4)
        circles = [c0, c1, c2, c3, c4]
        for circle in circles:
            gui2.add(circle)
        c0.reposition(G_WIDTH, G_HEIGHT/2)
        c1.reposition(G_WIDTH/4, G_HEIGHT/4)
        c2.reposition(G_WIDTH/4+G_WIDTH/2, G_HEIGHT/4)
        c3.reposition(G_WIDTH/4, G_HEIGHT/4+G_HEIGHT/2)
        c4.reposition(G_WIDTH/4+G_WIDTH/2, G_HEIGHT/4+G_HEIGHT/2)
        return circles

    circles = make_initial_circles()
    change_performer = TogglePerformer("Change Selected to Performer", circles=circles)
    save_locations = SaveLocations("change location", circles=circles)
    grid.add(0,0, change_performer)
    grid.add(0,1, save_locations)
    gui.add(grid)
    return (window, window2, gui)
#grid.add(1,1, v)
if __name__ == "__main__":
    window, window2, gui = control_panel()
    pyglet.app.run()
