#!/usr/bin/python

#from constants import *
################################################################################
# Dump of base.py for shedskin - avoid looped includes base.hpp<->Final.hpp
#from base import Grid, Ant

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
STEPS = 680

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
PHER_OBSTACLE = "o"
FRINGE = "F"
START_FRINGE = "B"
COVER_FRINGE = "C"
SEARCH = "S"
BACKTRACK = "B"
FOUND_PHER = "F"

NOT_FOUND = 0
FOUND_PHEROMONE_MASTER = 1
FOUND_PHEROMONE_SERVANT = 2
FOUND_BASE = 3
PHER_ARROW = 0
PHER_ANT = 1
PHER_ID = 2
PHER_FRINGE = 3
NUM = 2
DEBUG = 0

arrow2num = {DOWN_SYM:DOWN, UP_SYM:UP, LEFT_SYM:LEFT, RIGHT_SYM:RIGHT}
num2arrow = dict([(v,k) for k,v in arrow2num.items()])

class GOAAnt(Ant):
    def __init__(self, symbol, location, ID, state, bfs):
        self.set_symbol(symbol)
        self.set_location(location)
        self.set_ID(ID)
        self.set_state(state)
        self.set_bfs(bfs)
        self._num_of_pheromones = 0
        self.set_radius()

    def get_symbol(self):
        return self._symbol

    def set_symbol(self, symbol):
        self._symbol = symbol

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

    def get_bfs(self):
        return self._bfs

    def set_bfs(self, bfs):
        self._bfs = bfs

    def get_radius(self):
        return self._radius

    def set_radius(self):
        """
        012
        7 3
        654
        """
        self._radius = (
            (self._location[0]-1,self._location[1]-1),
            (self._location[0]-1,self._location[1]),
            (self._location[0]-1,self._location[1]+1),
            (self._location[0],self._location[1]+1),
            (self._location[0]+1,self._location[1]+1),
            (self._location[0]+1,self._location[1]),
            (self._location[0]+1,self._location[1]-1),
            (self._location[0],self._location[1]-1))

    def inc_num_of_pheromones(self):
        self._num_of_pheromones+=1

    def get_num_of_pheromones(self):
        return self._num_of_pheromones

# unused according to shedskin

#    def print_radius(self):
#        radius = self.get_radius()
#        location = self.get_location()
#        print radius[0],radius[1],radius[2]
#        print radius[7],location,radius[3]
#        print radius[6],radius[5],radius[4]
#        print " "


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
        self._for_arrow = EMPTY
        self._direction = 0

    def set_obstacle(self):
        self._back_arrow = OBSTACLE
        self._ant_sym = OBSTACLE
        self._ant_ID = OBSTACLE
        self._for_arrow = OBSTACLE
        self._direction = -1

    def set_pher_obstacle(self):
        self._back_arrow = PHER_OBSTACLE
        self._ant_sym = PHER_OBSTACLE
        self._ant_ID = PHER_OBSTACLE
        self._for_arrow = PHER_OBSTACLE
        self._direction = -1

    def set_cell(self, back_arrow, ant_sym, ant_ID, for_arrow, direction):
        #assert((back_arrow == EMPTY and for_arrow == EMPTY) or ant_ID in '12')
        #if self._back_arrow == START and back_arrow != START:
        #    import pdb; pdb.set_trace()
        self._back_arrow = back_arrow
        self._ant_sym = ant_sym
        self._ant_ID = ant_ID
        self._for_arrow = for_arrow
        self._direction = direction

    def get_direction(self):
        return self._direction

    def set_direction(self, direction):
        self._direction = direction

    def inc_direction(self):
        self._direction = (self._direction+1)%4
        return self._direction

    def get_ant_sym(self):
        return self._ant_sym

    def set_ant_sym(self, ant_sym):
        self._ant_sym = ant_sym

    def get_ant_ID(self):
        return self._ant_ID

    def get_for_arrow(self):
        return self._for_arrow

    def set_for_arrow(self, for_arrow):
        self._for_arrow = for_arrow

    def get_back_arrow(self):
        return self._back_arrow

    def string_cell(self):
        return "".join((self._back_arrow, self._ant_sym, self._ant_ID, self._for_arrow))

# Unused according to shedskin

#    def is_empty(self):
#        return self._ant_sym != OBSTACLE
#
#    def dec_direction(self):
#        self._direction = (self._direction-1)%4
#        return self._direction
#
#    def set_ant_ID(self, ant_ID):
#        self._ant_ID = ant_ID
#
#    def set_back_arrow(self, back_arrow):
#        self._back_arrow = back_arrow

class GOAGrid(Grid):
    def __init__(self, board_size):
        super(GOAGrid, self).__init__(board_size = board_size)

    def init_grid(self):
        self._grid = [[self.make_cell() for j in xrange(self.size[1])]
                        for i in xrange(self.size[0])]
        self.empty = self.make_cell() # default empty cell to return for out of range checks (TODO: make immutable)
        self.obstacle = self.make_cell()

    def get(self, k):
        """ shedskin doesn't export this unless we explicitly define
        the inheriting function """
        return super(GOAGrid, self).get(k)

    def make_cell(self):
        return Cell(self)

#    def get_ant_location(self, i):
#        return self.ants[i].get_location()

    def place_ant_on_grid(self, ant, location):
        ant_i = int(ant.get_symbol()) - 1
        self.get(location).set_cell(back_arrow=START, ant_ID=ant.get_symbol(),
                    ant_sym=ANT, for_arrow=EMPTY, direction=0)
        self.ant_locations[ant_i] = location
        self.ant_homes[ant_i] = location
        self.ants[ant_i] = ant

    def create_obstacle(self, x, y, lenx, leny):
        for i in range(y, y+leny):
            for j in range(x, x+lenx):
                if self.has_key((i,j)):
                    self.get((i,j)).set_obstacle()

    def step(self, ant):
        old_location = self.get(ant.get_location())
        if is_ant_in_radius(self, ant):
            return 1
        elif ant.get_bfs()==FOUND_PHER:
            if not old_location.get_back_arrow()==START:
                follow_arrow(self, ant)
        elif ant.get_bfs()==SEARCH:
            ant_pheromone = is_pal_in_radius(self, ant)
            direction = old_location.get_direction()
            if ant_pheromone:
                if ant.get_ID() > int(self.get(ant_pheromone[0]).get_ant_ID()):
                    ant.set_state(FOUND_PHEROMONE_MASTER)
                    side = (ant_pheromone[1]-1)/2
                    move(self, ant, side, EMPTY)
                    ant.set_bfs(FOUND_PHER)
                else:
                    ant.set_state(FOUND_PHEROMONE_SERVANT)
                    ant.set_bfs(FOUND_PHER)
            else:
                direction = get_next(self, ant)
                c = self.get(ant.get_location())
                c.set_direction(direction)
                c.set_for_arrow(get_for_pheromone(direction))
                move(self, ant, direction, get_back_pheromone(direction))
                if is_ant_in_radius(self, ant):
                    return 1
                if is_pal_in_radius(self, ant):
                    ant.set_bfs(SEARCH)

        elif ant.get_bfs()==BACKTRACK:
            if is_blocked(self, ant):
                if DEBUG:
                    print "BLOCKED"
                if old_location.get_back_arrow() == START:
                    direction = get_next(self, ant)
                    move(self, ant, direction, START)
                else:
                    follow_arrow(self, ant)
                old_location.set_pher_obstacle()
            else:
                follow_arrow(self, ant)
                if DEBUG:
                    print "ant location: ", ant.get_location()
                original_direction = old_location.get_direction()
                new_direction = get_next(self, ant)
                old_location.set_direction(original_direction)
                if old_location.get_back_arrow()==START or \
                    not get_first(self, ant) == new_direction:
                    ant.set_bfs(SEARCH)
# unused according to shedskin

#    def get_ant_home(self, i):
#        return self.ant_homes[i]



def get_back_pheromone(move):
    if move == 0:
        return DOWN_SYM
    elif move == 1:
        return LEFT_SYM
    elif move == 2:
        return UP_SYM
    elif move == 3:
        return RIGHT_SYM

def get_for_pheromone(move):
    if move == 0:
        return UP_SYM
    elif move == 1:
        return RIGHT_SYM
    elif move == 2:
        return DOWN_SYM
    elif move == 3:
        return LEFT_SYM

# the actual movement of the ant
def move(grid, ant, side, pheromone):
    ant.set_radius()
    radius = ant.get_radius()
    location = ant.get_location()
    symbol = ant.get_symbol()
    old_cell = grid.get(location)
    assert(not old_cell.is_obstacle())
    # removing ant symbol from old cell
    old_cell.set_ant_sym(EMPTY)
    old_cell.inc_direction()
    old_cell.set_for_arrow(num2arrow[old_cell.get_direction()])
    new_location = radius[2*side + 1]
    ant.set_location(new_location)
    ant.set_radius()
    # we place the ant in the new location
#    print "new location is ",new_location
#    print "pheromones are ", pheromones
    assert(grid.get(new_location).is_obstacle() == False)
    if pheromone == EMPTY or not grid.get(ant.get_location()).get_back_arrow() == EMPTY:
		grid.get(new_location).set_ant_sym(ANT)
    else:
        ant.inc_num_of_pheromones()
        grid.get(new_location).set_cell(
            back_arrow=pheromone, ant_sym=ANT,
            ant_ID=symbol, for_arrow=pheromone, direction=arrow2num[pheromone])

# Backtracking
def follow_arrow (grid, ant):
    if DEBUG:
        print "ant location: ", ant.get_location()
    ant.set_radius()
    radius = ant.get_radius()
    location = ant.get_location()
    grid.get(location).set_ant_sym(EMPTY)
    if grid.get(location).get_back_arrow() == UP_SYM:
        if DEBUG:
            print "up"
        ant.set_location(radius[1])
    elif grid.get(location).get_back_arrow() == RIGHT_SYM:
        if DEBUG:
            print "right"
        ant.set_location(radius[3])
    elif grid.get(location).get_back_arrow() == DOWN_SYM:
        if DEBUG:
            print "down"
        ant.set_location(radius[5])
    elif grid.get(location).get_back_arrow() == LEFT_SYM:
        if DEBUG:
            print "left"
        ant.set_location(radius[7])
    ant.set_radius()
    new_location = ant.get_location()
    grid.get(new_location).set_ant_sym(ANT)
    if is_ant_in_radius(grid, ant):
        return 1
    if DEBUG:
        print "ant location: ", ant.get_location()

# unused according to shedskin

#def is_obstacle(grid, ant, side):
#    radius = ant.get_radius()
#    if grid[radius[2*side+1][0],radius[2*side+1][1]].get_back_arrow() == OBSTACLE \
#        or grid[radius[2*side+1][0],radius[2*side+1][1]].get_back_arrow() == PHER_OBSTACLE:
#        return 1
#    return 0
#
#def is_empty(grid, ant, side):
#    radius = ant.get_radius()
#    x, y = radius[2*side+1]
#    back_arrow = grid.get((x, y)).get_back_arrow()
#    #print "side = %s, x = %s, y = %s, back_arrow = %s, grid.get((x,y)) = %s" % (side,
#    #    x, y, back_arrow, grid.get((x, y)))
#    if back_arrow == EMPTY:
#        return 1
#    return 0
#
#def is_pheromone_in_side(grid, ant, side, pheromone, type):
#    radius = ant.get_radius()
#    if (type == PHER_ARROW):
#        if grid.get(radius[side*2+1]).get_back_arrow() == pheromone:
#            return 1
#    elif (type == PHER_ANT):
#        if grid.get(radius[side*2+1]).get_ant_sym() == pheromone:
#            return 1
#    elif (type == PHER_ID):
#        if grid.get(radius[side*2+1]).get_ant_ID() == pheromone:
#            return 1
#    elif (type == PHER_FRINGE):
#        if grid.get(radius[side*2+1]).get_for_arrow() == pheromone:
#            return 1
#    return 0
#
#def set_pheromone(grid, ant, pheromone, type):
#    location = grid.get(ant.get_location())
#    if type == PHER_ARROW:
#        grid[location] = (pheromone, grid[location][1], grid[location][2], grid[location][3])
#    elif type == PHER_ANT:
#        grid[location] = (grid[location][0], pheromone, grid[location][2], grid[location][3])
#    elif type == PHER_ID:
#        grid[location] = (grid[location][0], grid[location][1], pheromone, grid[location][3])
#    elif type == PHER_FRINGE:
#        grid[location] = (grid[location][0], grid[location][1], grid[location][2], pheromone)
#

def is_blocked_side(grid, ant, side):
    ant.set_radius()
    radius = ant.get_radius()
    cell = grid.get((radius[2*side+1][0],radius[2*side+1][1]))
    if DEBUG:
        print "blocked?", cell.get_back_arrow()
    return (cell.get_back_arrow() == EMPTY
        or cell.get_back_arrow() == get_back_pheromone(side)
        or cell.get_for_arrow() == get_back_pheromone(side)
        or cell.is_obstacle())

def is_blocked(grid, ant):
    ant.set_radius()
    radius = ant.get_radius()
    count = 0
    for direction in range(0,4):
        if is_blocked_side(grid, ant, direction):
            count += 1
    if DEBUG:
        print "count", count
    if count == 3:
        return 1
    return 0

def is_ant_in_radius(grid, ant):
    radius = ant.get_radius()
    for i in range(0,8):
        if grid.get(radius[i]).get_ant_sym() == ANT:
            return 1
    return 0

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

def get_first(grid, ant):
    location = grid.get(ant.get_location())
    radius = ant.get_radius()
    direction = location.get_direction()
    back = get_backtrack(grid, ant)
    for new_direction in range(0,4):
        new_direction = (new_direction+1)%4
        if not new_direction == back:
            back_arrow = grid.get((radius[2*new_direction+1][0],
                                  radius[2*new_direction+1][1]
                                 )).get_back_arrow()
            if back_arrow == EMPTY or back_arrow == get_back_pheromone(new_direction):
                return new_direction

def get_backtrack(grid, ant):
    back = grid.get(ant.get_location()).get_back_arrow()
    if back == UP_SYM:
        return 0
    elif back == RIGHT_SYM:
        return 1
    elif back == DOWN_SYM:
        return 2
    elif back == LEFT_SYM:
        return 3
    else:
        return -1

def get_next(grid, ant):
    location = grid.get(ant.get_location())
    radius = ant.get_radius()
    new_direction = location.get_direction()
    back = get_backtrack(grid, ant)
    count = 0
    while True:
        back_arrow = grid.get((radius[2*new_direction+1][0],
                              radius[2*new_direction+1][1])).get_back_arrow()
        if back_arrow == EMPTY or back_arrow == START or location.get_back_arrow() == num2arrow[new_direction] or back_arrow == get_back_pheromone(new_direction):
            return new_direction
        new_direction = (new_direction+1)%4
        count += 1
        assert(count<4)

def make_ants(ant_locations):
    return [GOAAnt(symbol=symbol, location=location, ID=the_id,
                         state=NOT_FOUND, bfs=SEARCH)
        for location, (symbol, the_id) in
            zip(ant_locations, [(ANT_SYMBOL_1, 1), (ANT_SYMBOL_2, 2)])]

def make_grid(board_size):
    return GOAGrid(board_size = board_size)

# for shedskin (TODO - get shedskin to use __all__)
if __name__ == '__main__':
    locations = ((3, 3), (4, 4))
    ants = make_ants(locations)
    get_for_pheromone(0)
    get_back_pheromone(0)
    a1=ants[0]
    a1.get_ID()
    a1.get_state()
    a1.get_bfs()
    a1.set_radius()
    a1.inc_num_of_pheromones()
    a1.get_num_of_pheromones()
    grid = make_grid([5,5])
    ants[0].print_radius()
    for i in xrange(len(ants)):
        grid.place_ant_on_grid(ants[i], locations[i])
    grid.create_walls() # from base.py
    grid.get((5,5))
    grid.has_key((5,5))
    grid.set_obstacles([(1,2),(3,4)])
    #grid.get_ant_locations()
    for ant in ants:
        grid.step(ant)
    grid.display()

