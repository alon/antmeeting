class LineWidth(object):
    pass

class style(object):
    @staticmethod
    def linewidth(width):
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
        self.grid = [[cell(self) for j in xrange(self.size[1])]
                        for i in xrange(self.size[0])]
        self.ant_locations = [None, None]
        self.ant_homes = [None, None]
        self.ants = [None, None]
        self.empty = cell(self) # default empty cell to return for out of range checks (TODO: make immutable)
        self.obstacle = cell(self)
        self.obstacle.set_obstacle()

    def create_walls(self):
        self.create_obstacle(0, 1, 1, self.size[0])
        self.create_obstacle(0, 0, self.size[1], 1)
        self.create_obstacle(1, self.size[0], self.size[1], 1)
        self.create_obstacle(self.size[1], 0, 1, self.size[0])

    # Dictionary protocol
    def __getitem__(self, k):
        y, x = k
        if y >= len(self.grid) or y < 0:
            return self.obstacle
        row = self.grid[y]
        if x >= len(row) or x < 0:
            return self.obstacle
        return row[x]

    def has_key(self, k):
        return (0 <= k[0] <= self.size[0]) and (0 <= k[1] <= self.size[1])

    def display(self, renderer = None, step_num = None):
        if renderer:
            renderer.render(self, title=str(step_num))
        for i in range(0, self.size[0]+1):
            for j in range(0, self.size[1]+1):
                print self[i,j],
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
            
    def get_ant_locations(self):
        return [tuple(self.get_ant_location(i)) for i in xrange(2)]

    def has_ant(self, i, j):
        return (i,j) in self.ant_locations()

class Ant(object):
    def print_radius(self):
        radius = self.get_radius()
        location = self.get_location()
        print radius[0],radius[1],radius[2]
        print radius[7],location,radius[3]
        print radius[6],radius[5],radius[4]
        print " "
     
