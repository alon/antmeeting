
class style(object):
    @staticmethod
    def linewidth(width):
        class LineWidth(object):
            pass
        lw = LineWidth()
        lw.width = width
        return lw


class Grid(object):

    def __init__(self, board_size, cell):
        """cell - class of cell instance
        board_size - tuple = (number of cols, number of rows) NOTE: inverse of usual convention.
        """
        self.render_size = board_size
        self.size = self.render_size
        self.grid = [[cell(self) for j in xrange(self.size[1]+1)]
                        for i in xrange(self.size[0]+1)]
        self.ant_locations = [None, None]
        self.ant_homes = [None, None]
        self.ants = [None, None]
        self.empty = cell(self) # default empty cell to return for out of range checks (TODO: make immutable)

    def create_walls(s):
        s.create_obstacle(0, 1, 1, s.size[0])
        s.create_obstacle(0, 0, s.size[1], 1)
        s.create_obstacle(1, s.size[0], s.size[1], 1)
        s.create_obstacle(s.size[1], 0, 1, s.size[0])

    # Dictionary protocol
    def __getitem__(self, k):
        if k[0] >= len(self.grid) or k[0] < 0: return self.empty
        row = self.grid[k[0]]
        if k[1] >= len(row) or k[1] < 0: return self.empty
        return row[k[1]]

    def has_key(self, k):
        return (0 <= k[0] <= self.size[0]) and (0 <= k[1] <= self.size[1])

    def display(s, pyx_renderer = None, step_num = None):
        if pyx_renderer:
            pyx_renderer.render(s, title=str(step_num))
        for i in range(0, s.size[0]+1):
            for j in range(0, s.size[1]+1):
                print s[i,j],
            print " "
        print " "

    # Drawing helpers (pyx)

    def draw_home(self, c, i, j):
        x, y = j, self.size[0] - i
        s = 0.1
        d = 0.4
        lw = 0.05
        slw = style.linewidth(0.05)
        for px, py, dx, dy in [(x - d, y - d, 1, 1),
            (x + d, y - d, -1, 1), (x - d, y + d, 1, -1),
            (x + d, y + d, -1, -1)]:
            c.stroke(path.line(px - lw*dx/2, py, px + s*dx, py), [slw])
            c.stroke(path.line(px, py - lw*dy/2, px, py + s*dy), [slw])

    def set_obstacles(self, obst_iter):
        for x, y in obst_iter:
            self[x, y].set_obstacle()
            

class Ant(object):
    def print_radius(ant):
        radius = ant.get_radius()
        location = ant.get_location()
        print radius[0],radius[1],radius[2]
        print radius[7],location,radius[3]
        print radius[6],radius[5],radius[4]
        print " "
     
