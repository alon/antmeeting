BOARD_SIZE = (20, 19)
STARTING_LOCATION_1 = (8,8)
STARTING_LOCATION_2 = (2,2)
STEPS = 680
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
#from constants import *
import time


class ant(object):
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

class cell(object):
    def __init__(self):
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
    
    
def init_grid():
    grid = {}
    for i in range(0, BOARD_SIZE[0]+1):
        for j in range(0, BOARD_SIZE[1]+1):
            #back arrow, ant, ID, for arrow 
            grid[i,j] = cell()
    return grid

def create_walls(grid):
    create_obstacle(grid, 0, 1, 1, BOARD_SIZE[0])
    create_obstacle(grid, 0, 0, BOARD_SIZE[1], 1)
    create_obstacle(grid, 1, BOARD_SIZE[0], BOARD_SIZE[1], 1)
    create_obstacle(grid, BOARD_SIZE[1], 0, 1, BOARD_SIZE[0])
    
def place_ant_on_grid(grid, ant, location):
    grid[location].set_cell(START, ANT, ant.get_symbol(), EMPTY, 0)    
     
def print_radius(ant):
    radius = ant.get_radius()
    location = ant.get_location()
    print radius[0],radius[1],radius[2]
    print radius[7],location,radius[3]
    print radius[6],radius[5],radius[4]
    print " "
    
def print_grid(grid):
    for i in range(0, BOARD_SIZE[0]+1):
        for j in range(0, BOARD_SIZE[1]+1):
            print grid[i,j].string_cell(),
        print " "
    print " "
    
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
    # removing ant symbol from old cell
    old_cell.set_ant_sym(EMPTY)
    new_location = radius[2*side + 1]
    ant.set_location(new_location)
    ant.set_radius()        
    # we place the ant in the new location
#    print "new location is ",new_location
#    print "pheromones are ", pheromones
    if pheromone == EMPTY:
        grid[new_location].set_ant_sym(ANT)
    else:
        grid[new_location].set_cell(pheromone, ANT, symbol, EMPTY, 0)
    
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
            
def create_obstacle(grid, x, y, lenx, leny):
    for i in range(y, y+leny):
        for j in range(x, x+lenx):
            grid[i,j].set_obstacle()
    
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
    if grid[radius[2*side+1][0],radius[2*side+1][1]].get_back_arrow() == EMPTY \
        or grid[radius[2*side+1][0],radius[2*side+1][1]].get_back_arrow() == get_back_pheromone(side) \
        or grid[radius[2*side+1][0],radius[2*side+1][1]].get_for_arrow() == get_back_pheromone(side):
        return 0
    return 1
    
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
#    print grid[ant.radius[2*side+1][0],ant.radius[2*side+1][1]]
    if grid[radius[2*side+1][0],radius[2*side+1][1]].get_back_arrow() == EMPTY:
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
        new_direction = location.inc_direction()
        back_arrow = grid[radius[2*new_direction+1][0],radius[2*new_direction+1][1]].get_back_arrow()
		if back_arrow == EMPTY or back_arrow == START or back_arrow == get_back_pheromone(new_direction):
	        return new_direction	
    
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
                
    
grid = init_grid()
create_walls(grid)
#create_obstacle(grid, BOARD_SIZE[0]/2+6, BOARD_SIZE[0]/2+6, 3, 3)
#create_obstacle(grid, 4, 4, 1, 11)
#create_obstacle(grid, 6, 2, 2, 2)
#create_obstacle(grid, 10, 10, 3, 3)
#create_obstacle(grid, 4, 10, 3, 3)
#create_obstacle(grid, 4, 4, 3, 3)
#create_obstacle(grid, 10, 4, 3, 3)
#create_obstacle(grid, 7, 8, 1, 1)
#create_obstacle(grid, 9, 8, 1, 1)
#create_obstacle(grid, 8, 9, 1, 1)
#create_obstacle(grid, 3, 3, 5, 5)
#create_obstacle(grid, 3, 9, 5, 5)
#create_obstacle(grid, 9, 9, 5, 5)
#create_obstacle(grid, 9, 3, 5, 5)
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
    print "step",i
else:
    print "NO MEETING!"
print_grid(grid)