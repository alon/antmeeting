BOARD_SIZE = (20, 19)
STARTING_LOCATION_1 = (8,8)
STARTING_LOCATION_2 = (2,2)
STEPS = 400
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

#from constants import *
import time


class ant(object):
    def __init__(self, symbol, location, ID, state, bfs):
        self._orientation = UP
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

    def get_bfs(self):
        return self._bfs
    
    def set_bfs(self, bfs):
        self._bfs = bfs
    
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

class cell(object):
    def __init__(self):
        self._arr_stack = [EMPTY]
        self._ant_sym = EMPTY
        self._ant_ID = EMPTY
        self._fringe = EMPTY
        self._pointer = 0
        
    def set_obstacle(self):
        self._arr_stack = [OBSTACLE]
        self._ant_sym = OBSTACLE
        self._ant_ID = OBSTACLE
        self._fringe = OBSTACLE
    
    def set_cell(self, arr_stack, ant_sym, ant_ID, fringe, pointer):
        self._arr_stack = [arr_stack]
        self._ant_sym = ant_sym
        self._ant_ID = ant_ID
        self._fringe = fringe
        self._pointer = pointer
    
    def get_pointer(self):
        return self._pointer
    
    def set_pointer(self, pointer):
        self._pointer = pointer    
    
    def inc_pointer(self):
        self._pointer+=1
    
    def dec_pointer(self):
        self._pointer-=1
    
    def get_ant_sym(self):
        return self._ant_sym
    
    def set_ant_sym(self, ant_sym):
        self._ant_sym = ant_sym
    
    def get_ant_ID(self):
        return self._ant_ID
    
    def set_ant_ID(self, ant_ID):
        self._ant_ID = ant_ID
    
    def get_fringe(self):
        return self._fringe
    
    def set_fringe(self, fringe):
        self._fringe = fringe
    
    def get_arr_stack(self):
        return self._arr_stack
    
    def set_arr_stack(self, arr_stack):
        self._arr_stack = arr_stack
        
    def add_arr_stack(self, element):
        self._arr_stack.append(element)
        self._pointer+=1
    
    def pop_arr_stack(self):
        self._pointer-=1
        return self._arr_stack.pop()
    
    def peek_arr_stack(self):
        return self._arr_stack[self._pointer]
    
    def arr_stack_size(self):
        return len(self._arr_stack)
    
    def string_cell(self):
        return "".join((self._arr_stack[self._pointer], self._ant_sym, self._ant_ID, self._fringe))
    
    
def init_grid():
    grid = {}
    for i in range(0, BOARD_SIZE[0]+1):
        for j in range(0, BOARD_SIZE[1]+1):
            #direction, ant, ID, fringe 
            grid[i,j] = cell()
    return grid
    
def place_ant_on_grid(grid, ant, location):
    grid[location].set_cell(START, ANT, ant.get_symbol(), EMPTY, 0)    
     
def print_radius(ant):
    radius = ant.get_radius()
    location = ant.get_location()
    print radius[0],radius[1],radius[2]
    print radius[7],location,radius[3]
    print radius[6],radius[5],radius[4]
    print " "
    
def set_orientation(ant,side):
    orientation = ant.get_orientation()
    ant.set_orientation((orientation + side) % 4)
    ant.set_radius()

def force_orientation(ant,side):
    orientation = ant.get_orientation()
    ant.set_orientation(side)
    ant.set_radius()
    
def print_grid(grid):
    for i in range(0, BOARD_SIZE[0]+1):
        for j in range(0, BOARD_SIZE[1]+1):
            print grid[i,j].string_cell(),
        print " "
    print " "
    
# the actual movement of the ant 
def move(grid, ant, side, pheromones):
    radius = ant.get_radius()
    location = ant.get_location()
    symbol = ant.get_symbol()
    
    old_cell = grid[location] 
    # removing ant symbol from old cell
    old_cell.set_ant_sym(EMPTY)
    new_location = radius[2*side + 1]
    ant.set_location(new_location)        
    set_orientation(ant,side)
    # we place the ant in the new location
#    print "new location is ",new_location
#    print "pheromones are ", pheromones
    if pheromones[0] == EMPTY:
        grid[new_location].set_ant_sym(ANT)
    else:
        grid[new_location].set_cell(pheromones[0], ANT, symbol, pheromones[1], 0)
    
# Backtracking         
def follow_arrow (grid, ant):
    radius = ant.get_radius()
    orientation = ant.get_orientation()
    location = ant.get_location()
    old_location = grid[location]
    grid[location].set_ant_sym(EMPTY)        
    if grid[location].peek_arr_stack() == UP_SYM:
#        print "up"
        ant.set_location(radius[(9 - 2*(orientation)) % 8])
        force_orientation(ant,UP)
    elif grid[location].peek_arr_stack() == RIGHT_SYM:
#        print "right"
        ant.set_location(radius[(11 - 2*(orientation)) % 8])
        force_orientation(ant,RIGHT)
    elif grid[location].peek_arr_stack() == DOWN_SYM:
#        print "down"
        ant.set_location(radius[(13 - 2*(orientation)) % 8])
        force_orientation(ant,DOWN)
    elif grid[location].peek_arr_stack() == LEFT_SYM:
#        print "left"
        ant.set_location(radius[(7 - 2*(orientation)) % 8])
        force_orientation(ant,LEFT)
    new_location = ant.get_location()
#    print "new location is ", new_location
    grid[new_location].set_ant_sym(ANT)
#    if old_location.arr_stack_size() > 1:
#        old_location.pop_arr_stack()
#    print ant.orientation
#    time.sleep(2)
            
def create_obstacle(grid, x, y, lenx, leny):
    for i in range(y, y+leny):
        for j in range(x, x+lenx):
            grid[i,j].set_obstacle()
    
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


def is_obstacle(grid, ant, side):
    radius = ant.get_radius()
    if grid[radius[2*side+1][0],radius[2*side+1][1]].peek_arr_stack() == OBSTACLE \
        or grid[radius[2*side+1][0],radius[2*side+1][1]].peek_arr_stack() == PHER_OBSTACLE:
        return 1
    return 0

def is_blocked_side(grid, ant, side):
    radius = ant.get_radius()
    if grid[radius[2*side+1][0],radius[2*side+1][1]].peek_arr_stack() == EMPTY \
        or grid[radius[2*side+1][0],radius[2*side+1][1]].peek_arr_stack() == get_back_pheromone(ant, side):
        return 0
    return 1
    
def is_blocked(grid, ant):
    radius = ant.get_radius()
    if is_blocked_side(grid, ant, RIGHT) and is_blocked_side(grid, ant, UP) and is_blocked_side(grid, ant, LEFT):
        return 1
    return 0
    
def is_empty(grid, ant, side):
    radius = ant.get_radius()
#    print grid[ant.radius[2*side+1][0],ant.radius[2*side+1][1]]
    if grid[radius[2*side+1][0],radius[2*side+1][1]].peek_arr_stack() == EMPTY:
        return 1
    return 0    

def dead_end(grid, ant):
    if is_empty(grid, ant, UP) or is_empty(grid, ant, RIGHT) or is_empty(grid, ant, LEFT): 
        return 0
    return 1

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
        if (grid[radius[i]].get_ant_ID() != ant.get_symbol()) and (grid[radius[i]].get_ant_ID() != EMPTY) and (grid[radius[i]].get_ant_ID() != OBSTACLE):
            return [radius[i],i]
    return 0
    
def is_pheromone_in_side(grid, ant, side, pheromone, type):
    radius = ant.get_radius()
    if (type == PHER_ARROW):
        if grid[radius[side*2+1]].peek_arr_stack() == pheromone:
            return 1
    elif (type == PHER_ANT):
        if grid[radius[side*2+1]].get_ant_sym() == pheromone:
            return 1
    elif (type == PHER_ID):
        if grid[radius[side*2+1]].get_ant_ID() == pheromone:
            return 1
    elif (type == PHER_FRINGE):
        if grid[radius[side*2+1]].get_fringe() == pheromone:
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
    
def step(grid, ant):
    if ant.get_bfs()==FOUND_PHER:
        if is_ant_in_radius(grid, ant):
            return 1
        elif not grid[ant.get_location()].peek_arr_stack()==START:
            follow_arrow(grid, ant)
    if ant.get_bfs()==SEARCH:
        ant_pheromone = is_pal_in_radius(grid, ant)
        if ant_pheromone != 0:  
#            print "FOUND PHEROMONE :",ant_pheromone
            if ant.get_ID() > int(grid[ant_pheromone[0]].get_ant_ID()):
#                print "master"
                ant.set_state(FOUND_PHEROMONE_MASTER)
                side = (ant_pheromone[1]-1)/2
#                print "side is ",side
                move(grid, ant, side, EMPTY)
                ant.set_bfs(FOUND_PHER)
            else:
#                print "servant"
                ant.set_state(FOUND_PHEROMONE_SERVANT)
                ant.set_bfs(FOUND_PHER)
        elif is_blocked(grid, ant):
            old_location = grid[ant.get_location()]
            follow_arrow(grid, ant)
            old_location.set_obstacle()
        elif is_empty(grid, ant, RIGHT):
            move(grid, ant, RIGHT, [get_back_pheromone(ant, RIGHT),EMPTY])
            ant.set_bfs(BACKTRACK)
        elif is_empty(grid, ant, DOWN):
            move(grid, ant, DOWN, [get_back_pheromone(ant, DOWN),EMPTY])
            ant.set_bfs(BACKTRACK)
        elif is_empty(grid, ant, LEFT):
            move(grid, ant, LEFT, [get_back_pheromone(ant, LEFT),EMPTY])
            ant.set_bfs(BACKTRACK)
        elif is_empty(grid, ant, UP):
            move(grid, ant, UP, [get_back_pheromone(ant, UP),EMPTY])
            ant.set_bfs(BACKTRACK)
        elif is_pheromone_in_side(grid, ant, RIGHT, get_back_pheromone(ant, RIGHT), PHER_ARROW):
            move(grid, ant, RIGHT, [get_back_pheromone(ant, RIGHT),EMPTY])
        elif is_pheromone_in_side(grid, ant, LEFT, get_back_pheromone(ant, LEFT), PHER_ARROW):
            move(grid, ant, LEFT, [get_back_pheromone(ant, LEFT),EMPTY])
        elif is_pheromone_in_side(grid, ant, UP, get_back_pheromone(ant, UP), PHER_ARROW):
            move(grid, ant, UP, [get_back_pheromone(ant, UP),EMPTY])
    elif ant.get_bfs()==BACKTRACK:
        if grid[ant.get_location()].peek_arr_stack()==START:
            ant.set_bfs(SEARCH)
        else:
            follow_arrow(grid, ant)
            
    
grid = init_grid()

#create_obstacle(grid, BOARD_SIZE[0]/2+6, BOARD_SIZE[0]/2+6, 3, 3)
#create_obstacle(grid, 4, 4, 1, 11)
#create_obstacle(grid, 6, 2, 2, 2)
#create_obstacle(grid, 10, 10, 3, 3)
#create_obstacle(grid, 4, 10, 3, 3)
create_obstacle(grid, 4, 4, 3, 3)
#create_obstacle(grid, 10, 4, 3, 3)
create_obstacle(grid, 5, 8, 1, 1)
create_obstacle(grid, 6, 6, 2, 2)
create_obstacle(grid, 6, 9, 2, 2)
create_obstacle(grid, 9, 9, 2, 2)
# 4 walls
create_obstacle(grid, 0, 1, 1, BOARD_SIZE[0])
create_obstacle(grid, 0, 0, BOARD_SIZE[1], 1)
create_obstacle(grid, 1, BOARD_SIZE[0], BOARD_SIZE[1], 1)
create_obstacle(grid, BOARD_SIZE[1], 0, 1, BOARD_SIZE[0])
# creating ants
ant_1 = ant(symbol=ANT_SYMBOL_1, location=STARTING_LOCATION_1, ID=1, state=NOT_FOUND, bfs=SEARCH)
ant_2 = ant(symbol=ANT_SYMBOL_2, location=STARTING_LOCATION_2, ID=2, state=NOT_FOUND, bfs=SEARCH)

place_ant_on_grid(grid, ant_1, STARTING_LOCATION_1)
place_ant_on_grid(grid, ant_2, STARTING_LOCATION_2)
print "ant 1 radius:"
print_radius(ant_1)
print "ant 2 radius:"
print_radius(ant_2)
print_grid(grid)
#print grid

for i in range(1,STEPS):
### Code for non anonymous ants
#    print grid[ant.radius[2*RIGHT+1][0],ant.radius[2*RIGHT+1][1]]
#    if (ant_1.get_state() != FOUND_BASE and step(grid, ant_1) == 1):
#        print "MEETING!"
#        break
#    if (ant_2.get_state() != FOUND_BASE and step(grid, ant_2) == 1):
#        print "MEETING!"
#        break
###    
    
    if (step(grid, ant_1) == 1):
        print "MEETING!"
        break
    if (step(grid, ant_2) == 1):
        print "MEETING!"
        break
    
    print_grid(grid)
else:
    print "NO MEETING!"
print_grid(grid)