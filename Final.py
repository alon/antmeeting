#!/usr/bin/python

#from constants import *
import time
from base import Grid, Ant

class color(object):
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    @staticmethod
    def rgb(r, g, b):
        return color(r, g, b)

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

class GOAAnt(Ant):
    def __init__(self, symbol, location, ID, state, bfs):
        self._symbol = symbol
        self._location = location
        self._ID = ID
        self._state = state
        self._bfs = bfs
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
        self._radius[0] = (self._location[0]-1,self._location[1]-1)
        self._radius[1] = (self._location[0]-1,self._location[1])
        self._radius[2] = (self._location[0]-1,self._location[1]+1)
        self._radius[3] = (self._location[0],self._location[1]+1)
        self._radius[4] = (self._location[0]+1,self._location[1]+1)
        self._radius[5] = (self._location[0]+1,self._location[1])
        self._radius[6] = (self._location[0]+1,self._location[1]-1)
        self._radius[7] = (self._location[0],self._location[1]-1)

    def print_radius(ant):
        radius = ant.get_radius()
        location = ant.get_location()
        print radius[0],radius[1],radius[2]
        print radius[7],location,radius[3]
        print radius[6],radius[5],radius[4]
        print " "

class cell(object):
    def __init__(self, board):
        self.set_empty()
        self.board = board

    def __str__(self):
        return self.string_cell()

    def is_empty(self):
        return self._ant_sym != OBSTACLE

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
        assert((back_arrow == EMPTY and for_arrow == EMPTY) or ant_ID in '12')
        if self._back_arrow == START and back_arrow != START:
            import pdb; pdb.set_trace()
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

    def dec_direction(self):
        self._direction = (self._direction-1)%4
        return self._direction

    def get_ant_sym(self):
        return self._ant_sym

    def set_ant_sym(self, ant_sym):
        self._ant_sym = ant_sym

    def get_ant_ID(self):
        return self._ant_ID

    def set_ant_ID(self, ant_ID):
        self._ant_ID = ant_ID

    def get_for_arrow(self):
        return self._for_arrow

    def set_for_arrow(self, for_arrow):
        self._for_arrow = for_arrow

    def get_back_arrow(self):
        return self._back_arrow

    def set_back_arrow(self, back_arrow):
        self._back_arrow = back_arrow

    def string_cell(self):
        return "".join((self._back_arrow, self._ant_sym, self._ant_ID, self._for_arrow))


class GOAGrid(Grid):
    def __init__(self, board_size):
        Grid.__init__(self, board_size = board_size, cell=cell)

    def get_ant_location(self, i):
        return self.ants[i].get_location()

    def get_ant_home(self, i):
        return self.ant_homes[i]

    def place_ant_on_grid(s, ant, location):
        ant_i = int(ant.get_symbol()) - 1
        s[location].set_cell(back_arrow=START, ant_ID=ant.get_symbol(),
                    ant_sym=ANT, for_arrow=EMPTY, direction=0)
        s.ant_locations[ant_i] = location
        s.ant_homes[ant_i] = location
        s.ants[ant_i] = ant

    def create_obstacle(s, x, y, lenx, leny):
        for i in range(y, y+leny):
            for j in range(x, x+lenx):
                if s.has_key((i,j)):
                    s[i,j].set_obstacle()

    def render_cell(self, cell, c, i, j):
        """ draw cell onto canvas """
        BOARD_SIZE = self.size
        # note that x and y are inverted, and that we put max_y - y to flip y
        x, y = j, BOARD_SIZE[0] - i
        grey = color.rgb(0.5,0.5,0.5)
        back_arrow = cell.get_back_arrow()
        cmds = []
        if cell.get_ant_sym() == ANT:
            # render the ant
            from render_to_pdf import render_ant
            cmds.append(('ant',
                lambda c=c, x=x, y=y: render_ant(c, x, y)))
        if back_arrow == START: # draw H
            #c.text(j, BOARD_SIZE[1] - i, 'H')
            cmds.append(('home',
                lambda c=c, self=self, i=i, j=j: self.draw_home(c, i, j)))
        elif back_arrow == OBSTACLE:
            assert(cell.get_ant_sym() == back_arrow)
            cmds.append(('obstacle',
                lambda c=c, x=x, y=y: c.fill(
                    path.rect(x - 0.25, y - 0.25, 0.5, 0.5))))
        elif back_arrow == PHER_OBSTACLE:
            assert(cell.get_ant_sym() == back_arrow)
            cmds.append(('pher_obstacle',
                lambda c=c, x=x, y=y: c.fill(
                    path.rect(x - 0.2, y - 0.2, 0.4, 0.4), [grey])))
        else:
            back_arrow = cell.get_back_arrow()
            if back_arrow in [UP_SYM, DOWN_SYM, LEFT_SYM, RIGHT_SYM]:
                dx, dy = {UP_SYM: (0, -1), DOWN_SYM: (0, 1), LEFT_SYM: (-1, 0), RIGHT_SYM: (1, 0)}[back_arrow]
                cmds.append(('arrow',
                    lambda c=c, x=x, y=y, dx=dx, dy=dy: c.stroke(
                    path.line(x, y, x + dx, y - dy), [deco.earrow(),
                    style.linewidth(0.05)])))
        return cmds

    def step(grid, ant):
        if ant.get_bfs()==FOUND_PHER:
            if is_ant_in_radius(grid, ant):
                return 1
            elif not grid[ant.get_location()].get_back_arrow()==START:
                follow_arrow(grid, ant)
        if ant.get_bfs()==SEARCH:
            ant_pheromone = is_pal_in_radius(grid, ant)
            direction = grid[ant.get_location()].get_direction()
            if ant_pheromone != 0:
                if ant.get_ID() > int(grid[ant_pheromone[0]].get_ant_ID()):
                    ant.set_state(FOUND_PHEROMONE_MASTER)
                    side = (ant_pheromone[1]-1)/2
                    move(grid, ant, side, EMPTY)
                    ant.set_bfs(FOUND_PHER)
                else:
                    ant.set_state(FOUND_PHEROMONE_SERVANT)
                    ant.set_bfs(FOUND_PHER)
            else:
                direction = get_next(grid, ant)
                grid[ant.get_location()].set_direction(direction)
                grid[ant.get_location()].set_for_arrow(get_for_pheromone(direction))
                move(grid, ant, direction, get_back_pheromone(direction))
                if is_ant_in_radius(grid, ant):
                    return 1
                if is_pal_in_radius(grid, ant) != 0:
                    ant.set_bfs(SEARCH)

        elif ant.get_bfs()==BACKTRACK:
            if is_blocked(grid, ant):
                if DEBUG:
                    print "BLOCKED"
                old_location = grid[ant.get_location()]

                if old_location.get_back_arrow() == START:
                    direction = get_next(grid, ant)
                    move(grid, ant, direction, START)
                else:
                    follow_arrow(grid, ant)
                old_location.set_pher_obstacle()
            else:
                follow_arrow(grid, ant)
                if DEBUG:
                    print "ant location: ", ant.get_location()
                original_direction = grid[ant.get_location()].get_direction()
                new_direction = get_next(grid, ant)
                grid[ant.get_location()].set_direction(original_direction)
                if grid[ant.get_location()].get_back_arrow()==START or \
                    not get_first(grid, ant) == new_direction:
                    ant.set_bfs(SEARCH)

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
    old_cell = grid[location]
    assert(not old_cell.is_obstacle())
    # removing ant symbol from old cell
    old_cell.set_ant_sym(EMPTY)
    new_location = radius[2*side + 1]
    ant.set_location(new_location)
    ant.set_radius()
    # we place the ant in the new location
#    print "new location is ",new_location
#    print "pheromones are ", pheromones
    assert(grid[new_location].is_obstacle() == False)
    if pheromone == EMPTY:
        grid[new_location].set_ant_sym(ANT)
    else:
        grid[new_location].set_cell(
            back_arrow=pheromone, ant_sym=ANT,
            ant_ID=symbol, for_arrow=EMPTY, direction=0)

# Backtracking
def follow_arrow (grid, ant):
    if DEBUG:
        print "ant location: ", ant.get_location()
    ant.set_radius()
    radius = ant.get_radius()
    location = ant.get_location()
    grid[location].set_ant_sym(EMPTY)
    if grid[location].get_back_arrow() == UP_SYM:
        if DEBUG:
            print "up"
        ant.set_location(radius[1])
    elif grid[location].get_back_arrow() == RIGHT_SYM:
        if DEBUG:
            print "right"
        ant.set_location(radius[3])
    elif grid[location].get_back_arrow() == DOWN_SYM:
        if DEBUG:
            print "down"
        ant.set_location(radius[5])
    elif grid[location].get_back_arrow() == LEFT_SYM:
        if DEBUG:
            print "left"
        ant.set_location(radius[7])
    ant.set_radius()
    new_location = ant.get_location()
#    print "new location is ", new_location
    grid[new_location].set_ant_sym(ANT)
    if DEBUG:
        print "ant location: ", ant.get_location()
#    if old_location.arr_stack_size() > 1:
#        old_location.pop_arr_stack()
#    print ant.orientation
#    time.sleep(2)


def is_obstacle(grid, ant, side):
    radius = ant.get_radius()
    if grid[radius[2*side+1][0],radius[2*side+1][1]].get_back_arrow() == OBSTACLE \
        or grid[radius[2*side+1][0],radius[2*side+1][1]].get_back_arrow() == PHER_OBSTACLE:
        return 1
    return 0

def is_blocked_side(grid, ant, side):
    ant.set_radius()
    radius = ant.get_radius()
    if DEBUG:
        print "blocked?", grid[radius[2*side+1][0],radius[2*side+1][1]].get_back_arrow()
    #or grid[radius[2*side+1][0],radius[2*side+1][1]].get_back_arrow() == get_back_pheromone(side)
    cell = grid[radius[2*side+1][0],radius[2*side+1][1]]
    if cell.is_obstacle() and radius[2*side+1][0] > len(grid.grid):
        import pdb; pdb.set_trace()
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

def is_empty(grid, ant, side):
    radius = ant.get_radius()
    x, y = radius[2*side+1]
    back_arrow = grid[x, y].get_back_arrow()
    #print "side = %s, x = %s, y = %s, back_arrow = %s, grid[x,y] = %s" % (side,
    #    x, y, back_arrow, grid[x, y])
    if back_arrow == EMPTY:
        return 1
    return 0

def is_ant_in_radius(grid, ant):
    radius = ant.get_radius()
    for i in range(0,8):
        if grid[radius[i]].get_ant_sym() == ANT:
            return 1
    return 0

def is_pal_in_radius(grid, ant):
    radius = ant.get_radius()
    #012
    #7 3
    #654
    for i in [1,3,5,7]:
        if (grid[radius[i]].get_ant_ID() != ant.get_symbol()) and (grid[radius[i]].get_ant_ID() != EMPTY) \
            and (grid[radius[i]].get_ant_ID() != OBSTACLE) and (grid[radius[i]].get_ant_ID() != PHER_OBSTACLE):
            return [radius[i],i]
    return 0

def is_pheromone_in_side(grid, ant, side, pheromone, type):
    radius = ant.get_radius()
    if (type == PHER_ARROW):
        if grid[radius[side*2+1]].get_back_arrow() == pheromone:
            return 1
    elif (type == PHER_ANT):
        if grid[radius[side*2+1]].get_ant_sym() == pheromone:
            return 1
    elif (type == PHER_ID):
        if grid[radius[side*2+1]].get_ant_ID() == pheromone:
            return 1
    elif (type == PHER_FRINGE):
        if grid[radius[side*2+1]].get_for_arrow() == pheromone:
            return 1
    return 0

def set_pheromone(grid, ant, pheromone, type):
    location = grid[ant.get_location()]
    if type == PHER_ARROW:
        grid[location] = (pheromone, grid[location][1], grid[location][2], grid[location][3])
    elif type == PHER_ANT:
        grid[location] = (grid[location][0], pheromone, grid[location][2], grid[location][3])
    elif type == PHER_ID:
        grid[location] = (grid[location][0], grid[location][1], pheromone, grid[location][3])
    elif type == PHER_FRINGE:
        grid[location] = (grid[location][0], grid[location][1], grid[location][2], pheromone)

def get_first(grid, ant):
    location = grid[ant.get_location()]
    radius = ant.get_radius()
    direction = location.get_direction()
    back = get_backtrack(grid, ant)
    for new_direction in range(0,4):
        new_direction = (new_direction+1)%4
        if not new_direction == back:
            back_arrow = grid[radius[2*new_direction+1][0],radius[2*new_direction+1][1]].get_back_arrow()
            if back_arrow == EMPTY or back_arrow == get_back_pheromone(new_direction):
                return new_direction
#    for new_direction in range(0,4):
#        new_direction = (new_direction+1)%4
#        if not new_direction == back:
#            back_arrow = grid[radius[2*new_direction+1][0],radius[2*new_direction+1][1]].get_back_arrow()
#            if back_arrow == get_back_pheromone(new_direction):
#                return new_direction
#
def get_backtrack(grid, ant):
    back = grid[ant.get_location()].get_back_arrow()
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
    location = grid[ant.get_location()]
    radius = ant.get_radius()
    old_direction = location.get_direction()
    back = get_backtrack(grid, ant)

    while True:
        new_direction = location.dec_direction()
        back_arrow = grid[radius[2*new_direction+1][0],radius[2*new_direction+1][1]].get_back_arrow()
        if back_arrow == EMPTY or back_arrow == START or back_arrow == get_back_pheromone(new_direction):
            return new_direction

