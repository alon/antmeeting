import time
#from Ants import (init_grid, create_obstacle, ant, place_ant_on_grid,
    #print_radius, print_grid)

class Grid(object):

    def __init__(self, board_size):
        """cell - class of cell instance
        board_size - tuple = (number of cols, number of rows) NOTE: inverse of usual convention.
        """
        self.render_size = board_size
        self.size = self.render_size
        self.ant_locations = [None, None]
        self.ant_homes = [None, None]
        self.ants = [None, None]
        self.init_grid() # implement by inheritaince
        self.obstacle.set_obstacle()

    def create_walls(self):
        self.create_obstacle(0, 1, 1, self.size[0])
        self.create_obstacle(0, 0, self.size[1], 1)
        self.create_obstacle(1, self.size[0], self.size[1], 1)
        self.create_obstacle(self.size[1], 0, 1, self.size[0])

    # Dictionary protocol
    def get(self, k):
        y, x = int(k[0]), int(k[1])
        if y >= len(self._grid) or y < 0:
            return self.obstacle
        row = self._grid[y]
        if x >= len(row) or x < 0:
            return self.obstacle
        return row[x]

    def has_key(self, k):
        y, x = int(k[0]), int(k[1])
        return (0 <= y <= self.size[0]) and (0 <= x <= self.size[1])

    def display(self, step_num = None):
        for i in range(0, self.size[0]+1):
            for j in range(0, self.size[1]+1):
                print self.get((i,j)),
            print " "
        print " "

    def set_obstacles(self, obst_iter):
        for x, y in obst_iter:
            self.get((x, y)).set_obstacle()

#    def get_ant_locations(self):
#        return [tuple(self.get_ant_location(i)) for i in xrange(2)]

class Ant(object):
    def print_radius(self):
        radius = self.get_radius()
        location = self.get_location()
        print radius[0],radius[1],radius[2]
        print radius[7],location,radius[3]
        print radius[6],radius[5],radius[4]
        print " "


################################################################################



# Parameters
#BOARD_SIZE = (20, 19)
#STARTING_LOCATION_1 = (8,8)
#STARTING_LOCATION_2 = (3,3)
STEPS = 160

# Constants
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
EMPTY = "_"
ANT_SYMBOL_1 = "1"
ANT_SYMBOL_2 = "2"
ANT = "*"
START = "H"
UP_SYM = "^"
RIGHT_SYM = ">"
DOWN_SYM = "V"
LEFT_SYM = "<"
OBSTACLE = "O"
NOT_FOUND = 0
FOUND_PHEROMONE_MASTER = 1
FOUND_PHEROMONE_SERVANT = 2
FOUND_BASE = 3
NUM = 2
FOUND_PHER = "F"
SEARCH = "S"
PHER_OBSTACLE = "o"

#from constants import *

class COAAnt(Ant):
    def __init__(self, symbol, location, ID, state):
        self._orientation = UP
        self._symbol = symbol
        self._location = location
        self._ID = ID
        self._state = state
        self._num_of_pheromones = 0
        #012
        #7 3
        #654
        self._radius = [(location[0]-1,location[1]-1),
              (location[0]-1,location[1]),
              (location[0]-1,location[1]+1),
              (location[0],location[1]+1),
              (location[0]+1,location[1]+1),
              (location[0]+1,location[1]),
              (location[0]+1,location[1]-1),
              (location[0],location[1]-1)
              ]

    def inc_num_of_pheromones(self):
        self._num_of_pheromones+=1

    def get_num_of_pheromones(self):
        return self._num_of_pheromones


    def get_symbol(self):
        return self._symbol

    def set_symbol(self, symbol):
        self._symbol = symbol

    def get_orientation(self):
        return self._orientation

    def set_orientation(self, orientation):
        self._orientation = orientation

    def get_location(self):
        return self._location

    def set_location(self, location):
        self._location = location

    def get_ID(self):
        return self._ID

    def set_ID(self, ID):
        self._ID = ID

    def get_state(self):
        return self._state

    def set_state(self, state):
        self._state = state

    def get_radius(self):
        return self._radius

    def set_radius(self):
        self._radius[0 - 2*self._orientation % 8] = (self._location[0]-1,self._location[1]-1)
        self._radius[1 - 2*self._orientation % 8] = (self._location[0]-1,self._location[1])
        self._radius[2 - 2*self._orientation % 8] = (self._location[0]-1,self._location[1]+1)
        self._radius[3 - 2*self._orientation % 8] = (self._location[0],self._location[1]+1)
        self._radius[4 - 2*self._orientation % 8] = (self._location[0]+1,self._location[1]+1)
        self._radius[5 - 2*self._orientation % 8] = (self._location[0]+1,self._location[1])
        self._radius[6 - 2*self._orientation % 8] = (self._location[0]+1,self._location[1]-1)
        self._radius[7 - 2*self._orientation % 8] = (self._location[0],self._location[1]-1)

def set_orientation(ant,side):
    orientation = ant.get_orientation()
    ant.set_orientation((orientation + side) % 4)
    ant.set_radius()

def force_orientation(ant,side):
    orientation = ant.get_orientation()
    ant.set_orientation(side)
    ant.set_radius()

# the actual movement of the ant
def move(grid, ant, side, pheromone):
    radius = ant.get_radius()
    location = ant.get_location()
    symbol = ant.get_symbol()
    old_cell = grid.get(location)
    old_cell.set_ant_sym(EMPTY)
    new_location = radius[2*side + 1]
    ant.set_location(new_location)
    set_orientation(ant,side)
    if pheromone == EMPTY:
        grid.get(new_location).set_ant_sym(ANT)
    else:
        ant.inc_num_of_pheromones()
        grid.get(new_location).set_cell(
            back_arrow=pheromone, ant_sym=ANT,
            ant_ID=symbol)

# Backtracking
def follow_arrow (grid, ant):
    radius = ant.get_radius()
    orientation = ant.get_orientation()
    location = ant.get_location()
    old_location = grid.get(location)
    grid.get(location).set_ant_sym(EMPTY)
    if grid.get(location).get_back_arrow() == UP_SYM:
        #print "up",ant.get_ID()
        ant.set_location(radius[(9 - 2*(orientation)) % 8])
        force_orientation(ant,UP)
    elif grid.get(location).get_back_arrow() == RIGHT_SYM:
        #print "right",ant.get_ID()
        ant.set_location(radius[(11 - 2*(orientation)) % 8])
        force_orientation(ant,RIGHT)
    elif grid.get(location).get_back_arrow() == DOWN_SYM:
        #print "down",ant.get_ID()
        ant.set_location(radius[(13 - 2*(orientation)) % 8])
        force_orientation(ant,DOWN)
    elif grid.get(location).get_back_arrow() == LEFT_SYM:
        #print "left",ant.get_ID()
        ant.set_location(radius[(7 - 2*(orientation)) % 8])
        force_orientation(ant,LEFT)
    new_location = ant.get_location()
    grid.get(new_location).set_ant_sym(ANT)
    if is_ant_in_radius(grid, ant):
        return 1


def get_back_pheromone(ant, move):
    orientation = ant.get_orientation()
    if (orientation + move) % 4 == 0:
        return DOWN_SYM
    elif (orientation + move) % 4 == 1:
        return LEFT_SYM
    elif (orientation + move) % 4 == 2:
        return UP_SYM
    elif (orientation + move) % 4 == 3:
        return RIGHT_SYM
#def is_pheromone_right(grid,ant):

#def circle_obstacle(grid, ant, side):
#    while is_obstacle(grid, ant, side) and is_empty(grid, ant, (side - 1 % 4)):
#        move(grid, ant, (side - 1 % 4), get_back_pheromone(ant, (side - 1 % 4)))

def empty(clazz):
    return clazz((EMPTY, EMPTY, EMPTY))

class Cell(object):
    def __init__(self, board):
        self.set_empty()
        self.board = board

    def __str__(self):
        return self.string_cell()

    def is_obstacle(self):
        return self._ant_sym == OBSTACLE

    def set_empty(self):
        self._back_arrow = EMPTY
        self._ant_sym = EMPTY
        self._ant_ID = EMPTY
        #self._for_arrow = EMPTY
        #self._direction = 0

    def set_obstacle(self):
        self._back_arrow = OBSTACLE
        self._ant_sym = OBSTACLE
        self._ant_ID = OBSTACLE
        #self._for_arrow = OBSTACLE
        #self._direction = -1

    def set_pher_obstacle(self):
        self._back_arrow = PHER_OBSTACLE
        self._ant_sym = PHER_OBSTACLE
        self._ant_ID = PHER_OBSTACLE
        #self._for_arrow = PHER_OBSTACLE
        #self._direction = -1

    def set_cell(self, back_arrow, ant_sym, ant_ID):#, for_arrow, direction):
        #assert((back_arrow == EMPTY and for_arrow == EMPTY) or ant_ID in '12')
        #if self._back_arrow == START and back_arrow != START:
        #    import pdb; pdb.set_trace()
        self._back_arrow = back_arrow
        self._ant_sym = ant_sym
        self._ant_ID = ant_ID
        #self._for_arrow = for_arrow
        #self._direction = direction

    #def get_direction(self):
    #    return self._direction

    #def set_direction(self, direction):
    #    self._direction = direction

    #def inc_direction(self):
    #    self._direction = (self._direction+1)%4
    #    return self._direction

    def get_ant_sym(self):
        return self._ant_sym

    def set_ant_sym(self, ant_sym):
        self._ant_sym = ant_sym

    def get_ant_ID(self):
        return self._ant_ID

    #def get_for_arrow(self):
    #    return self._for_arrow

    #def set_for_arrow(self, for_arrow):
    #    self._for_arrow = for_arrow

    def get_back_arrow(self):
        return self._back_arrow

    def string_cell(self):
        return "".join((self._back_arrow, self._ant_sym, self._ant_ID))#, self._for_arrow))

class COAGrid(Grid):

    def __init__(self, board_size):
        Grid.__init__(self, board_size=board_size)

    def init_grid(self):
        self._grid = [[self.make_cell() for j in xrange(self.size[1])]
                        for i in xrange(self.size[0])]
        self.empty = self.make_cell() # default empty cell to return for out of range checks (TODO: make immutable)
        self.obstacle = self.make_cell()

    #def __setitem__(self, key, new_item):
    #   self.grid[key[0]][key[1]] = cell(new_item)

    def get(self, k):
        """ shedskin doesn't export this unless we explicitly define
        the inheriting function """
        return Grid.get(self, k)

    def make_cell(self):
        return Cell(self)

    def create_obstacle(self, x, y, lenx, leny):
        for i in range(y, y+leny):
            for j in range(x, x+lenx):
                if self.has_key((i,j)):
                    self.get((i,j)).set_obstacle()

    def get_ant_location(self, i):
        return self.ants[i].get_location()

    def get_ant_home(self, i):
        return self.ant_homes[i]

    def place_ant_on_grid(self, ant, location):
        ant_i = int(ant.get_symbol()) - 1
        self.get(location).set_cell(back_arrow=START, ant_ID=ant.get_symbol(),
                    ant_sym=ANT)#, for_arrow=EMPTY, direction=0)
        self.ant_locations[ant_i] = location
        self.ant_homes[ant_i] = location
        self.ants[ant_i] = ant

    def step(self, ant):
        old_location = self.get(ant.get_location())
        if is_ant_in_radius(self, ant):
            return 1
        ant_pheromone = is_pal_in_radius(self, ant)
        if is_ant_in_radius(self, ant):
            return 1
        elif ant.get_state()==FOUND_PHER:
            if not old_location.get_back_arrow()==START:
                follow_arrow(self, ant)
        elif ant.get_state()==SEARCH:
            ant_pheromone = is_pal_in_radius(self, ant)
            #direction = old_location.get_direction()
            if ant_pheromone:
                if ant.get_ID() > int(self.get(ant_pheromone[0]).get_ant_ID()):
                    #ant.set_state(FOUND_PHEROMONE_MASTER)
                    side = (ant_pheromone[1]-1)/2
                    move(self, ant, side, EMPTY)
                    ant.set_state(FOUND_PHER)
                else:
                    #ant.set_state(FOUND_PHEROMONE_SERVANT)
                    follow_arrow(self, ant)
                    ant.set_state(FOUND_PHER)
            else:#elif ant.get_state() == NOT_FOUND:
                if dead_end(self,ant):
                    if old_location.get_back_arrow()==START:
                        set_orientation(ant, DOWN)
                    else:
                        follow_arrow(self, ant)
                elif is_empty(self,ant, RIGHT):
                    move(self, ant, RIGHT, get_back_pheromone(ant,RIGHT))
                elif is_obstacle(self,ant, RIGHT) and is_empty(self,ant, UP):
            #        circle_obstacle(self, ant, RIGHT)
                    move(self, ant, UP, get_back_pheromone(ant, UP))
                elif is_obstacle(self,ant, UP):
                    move(self, ant, LEFT, get_back_pheromone(ant, LEFT))
                elif is_empty(self,ant, UP):
                    move(self, ant, UP, get_back_pheromone(ant,UP))
                elif is_empty(self,ant, LEFT):
                    move(self, ant, LEFT, get_back_pheromone(ant,LEFT))
                else:
                    print "problem?"

"""
        if ant.get_state() == NOT_FOUND and ant_pheromone != 0:
    #        print "ant pheromone", ant_pheromone
            if ant.get_ID() > int(self[ant_pheromone[0]][2]):
    #            print "master"
                ant.set_state(FOUND_PHEROMONE_MASTER)
                side = (ant_pheromone[1]-1)/2
    #            print side
                move(self, ant, side, EMPTY)
            else:
    #            print "servant"
                ant.set_state(FOUND_PHEROMONE_SERVANT)
                follow_arrow(self, ant)

                elif ant.get_state() == FOUND_PHEROMONE_MASTER:
            location = ant.get_location()
            if self[location][0] == "H":
                ant.set_state(FOUND_BASE)
            else:
                follow_arrow(self, ant)
            #follow trail to other base
        elif ant.get_state() == FOUND_PHEROMONE_SERVANT:
            follow_arrow(self, ant)
    #        print "following"
            #follow trail to base
        return 0
"""

def is_obstacle(grid,ant,side):
    radius = ant.get_radius()
    if grid.get((radius[2*side+1][0],radius[2*side+1][1])).get_back_arrow() == OBSTACLE:
        return 1
    return 0

def is_empty(grid,ant,side):
    radius = ant.get_radius()
#    print self[ant.radius[2*side+1][0],ant.radius[2*side+1][1]]
    if grid.get((radius[2*side+1][0],radius[2*side+1][1])).get_back_arrow() == EMPTY:
        return 1
    return 0

def dead_end(grid, ant):
    if is_empty(grid,ant, UP) or is_empty(grid,ant, RIGHT) or is_empty(grid,ant, LEFT):
        return 0
    return 1


def is_pal_in_radius(grid, ant):
    radius = ant.get_radius()
    #012
    #7 3
    #654
    for i in [1, 3, 5, 7]:
        if ((grid.get(radius[i]).get_ant_ID() != ant.get_symbol()) and
            (grid.get(radius[i]).get_ant_ID() != EMPTY) and
            (grid.get(radius[i]).get_ant_ID() != OBSTACLE) and
            (grid.get(radius[i]).get_ant_ID() != PHER_OBSTACLE)):
            return radius[i], i
    return None

def is_ant_in_radius(grid, ant):
    radius = ant.get_radius()
    for i in range(0, 8):
        if grid.get(radius[i]).get_ant_sym() == ANT:
            return True
    return False

def make_ants(ant_locations):
    return [COAAnt(symbol=symbol, location=location, ID=the_id,
                         state=SEARCH)
        for location, (symbol, the_id) in
            zip(ant_locations, [(ANT_SYMBOL_1, 1), (ANT_SYMBOL_2, 2)])]

def make_grid(board_size):
    return COAGrid(board_size = board_size)

def test():
    locations = ((3, 3), (6, 6))
    ants = make_ants(locations)
    get_back_pheromone(ants[0], 0)
    a1=ants[0]
    a1.get_ID()
    a1.get_state()
    a1.set_radius()
    a1.inc_num_of_pheromones()
    a1.get_num_of_pheromones()
    a1.set_symbol(ANT_SYMBOL_2)
    a1.set_ID(1)

    grid = make_grid([10,10])
    cell = grid.get(a1.get_location())
    cell.is_obstacle()
    cell.set_pher_obstacle()
    ants[0].print_radius()
    for i in xrange(len(ants)):
        grid.place_ant_on_grid(ants[i], locations[i])
    grid.get_ant_location(1)
    grid.get_ant_home(1)
    grid.create_walls() # from base.py
    grid.get((5,5))
    grid.has_key((5,5))
    grid.set_obstacles([(1,2),(3,4)])
    #grid.get_ant_locations()
    for i in xrange(10):
        for ant in ants:
            grid.step(ant)
        grid.display()

if __name__ == '__main__':
    test()
