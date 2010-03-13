BOARD_SIZE = (20, 20)
STARTING_LOCATION_1 = (7,7)
STARTING_LOCATION_2 = (3,3)
STEPS = 120
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
NUM = 2

#from constants import *
import time


class ant(object):
    def __init__(self, symbol, location):
        self._orientation = UP
        self._symbol = symbol
        self._location = location
        #123
        #804
        #765
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

def init_grid():
    grid = {}
    for i in range(0, BOARD_SIZE[0]+1):
        for j in range(0, BOARD_SIZE[1]+1):
            #direction, current, number 
            grid[i,j] = (EMPTY,EMPTY,EMPTY)
    return grid
    
def place_ant_on_grid(grid, ant, location):
    grid[(location)] = (START, ANT, ant.get_symbol())    
     
#def ant_update_radius(ant):
#    print ant.location, 
#    print " is the ant " + ant.symbol + " location"
#    ant.radius[0 - 2*ant.orientation % 8] = (ant.location[0]-1,ant.location[1]-1)
#    ant.radius[1 - 2*ant.orientation % 8] = (ant.location[0]-1,ant.location[1])
#    ant.radius[2 - 2*ant.orientation % 8] = (ant.location[0]-1,ant.location[1]+1)
#    ant.radius[3 - 2*ant.orientation % 8] = (ant.location[0],ant.location[1]+1)
#    ant.radius[4 - 2*ant.orientation % 8] = (ant.location[0]+1,ant.location[1]+1)
#    ant.radius[5 - 2*ant.orientation % 8] = (ant.location[0]+1,ant.location[1])
#    ant.radius[6 - 2*ant.orientation % 8] = (ant.location[0]+1,ant.location[1]-1)
#    ant.radius[7 - 2*ant.orientation % 8] = (ant.location[0],ant.location[1]-1)
#    return ant.radius

def print_radius(ant):
    radius = ant.get_radius()
    location = ant.get_location()
    print radius[0],radius[1],radius[2]
    print radius[7],location,radius[3]
    print radius[6],radius[5],radius[4]
    print " "
    
#def toggle_orientation_clockwise(ant):
#    ant.orientation = (ant.orientation + 1) % 4
#    ant_update_radius(ant)
    
def set_orientation(ant,side):
    orientation = ant.get_orientation()
    ant.set_orientation((orientation + side) % 4)
    ant.set_radius()

def force_orientation(ant,side):
    orientation = ant.get_orientation()
    ant.set_orientation(side)
    ant_update_radius(ant)
    
def print_grid(grid):
    for i in range(0, BOARD_SIZE[0]+1):
        for j in range(0, BOARD_SIZE[1]+1):
            print "".join(grid[i,j]),    
        print " "
    print " "
 
def move(grid, ant, side, pheromone):
    radius = ant.get_radius()
    location = ant.get_location()
    symbol = ant.get_symbol()
    old_location = grid[location] 
    grid[location] = (old_location[0], EMPTY, old_location[2])    
    new_location = radius[2*side + 1]
    ant.set_location(new_location)        
    set_orientation(ant,side)
    grid[new_location] = (pheromone, ANT, symbol)
    
#    print_radius(ant)
        
def follow_arrow (grid, ant):
    radius = ant.get_radius()
    orientation = ant.get_orientation()
    location = ant.get_location()
    old_location = grid[location]
    grid[location] = (old_location[0], EMPTY, old_location[2])        
    if grid[location].find(UP_SYM) > -1:
#        print "up"
        ant.set_location(radius[(9 - 2*(orientation)) % 8])
        force_orientation(ant,UP)
    elif grid[location].find(RIGHT_SYM) > -1:
#        print "right"
        ant.set_location(radius[(11 - 2*(orientation)) % 8])
        force_orientation(ant,RIGHT)
    elif grid[location].find(DOWN_SYM) > -1:
#        print "down"
        ant.set_location(radius[(13 - 2*(orientation)) % 8])
        force_orientation(ant,DOWN)
    elif grid[location].find(LEFT_SYM) > -1:
#        print "left"
        ant.set_location(radius[(7 - 2*(orientation)) % 8])
        force_orientation(ant,LEFT)
    new_location = ant.get_location()
    grid[new_location] = (new_location[0], ANT, new_location[2])
#    print ant.orientation
#    time.sleep(2)
            
def create_obstacle(grid,x,y,lenx,leny):
    for i in range(y, y+leny):
        for j in range(x, x+lenx):
            grid[i,j] = (OBSTACLE,OBSTACLE,OBSTACLE)
    
def get_back_pheromone(ant,move):
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

def is_obstacle(grid,ant,side):
    radius = ant.get_radius()
    if grid[radius[2*side+1][0],radius[2*side+1][1]][0] == OBSTACLE:
        return 1
    return 0
    
def is_empty(grid,ant,side):
    radius = ant.get_radius()
#    print grid[ant.radius[2*side+1][0],ant.radius[2*side+1][1]]
    if grid[radius[2*side+1][0],radius[2*side+1][1]][0] == EMPTY:
        return 1
    return 0    

def dead_end(grid, ant):
    if is_empty(grid, ant, UP) or is_empty(grid, ant, RIGHT) or is_empty(grid, ant, LEFT): 
        return 0
    return 1

def is_ant_in_radius(grid, ant):
    radius = ant.get_radius()
    for i in range(0,8):
#        if (grid(radius[i])[2] != ant.get_symbol()) and (grid(radius[i])[2] != EMPTY) and (grid(radius[i])[2] != OBSTACLE):
        if grid[radius[i]][1] == ANT:
            return 1
    return 0
    
def step(grid, ant):
    if is_ant_in_radius(grid, ant):
        return 1
    elif dead_end(grid, ant):
#        set_orientation(ant, DOWN)
        follow_arrow(grid, ant)
    elif is_empty(grid, ant, RIGHT):
        move(grid, ant, RIGHT, get_back_pheromone(ant,RIGHT))
    elif is_obstacle(grid, ant, RIGHT) and is_empty(grid, ant, UP):
#        circle_obstacle(grid, ant, RIGHT)
        move(grid, ant, UP, get_back_pheromone(ant, UP))
    elif is_obstacle(grid, ant, UP):
        move(grid, ant, LEFT, get_back_pheromone(ant, LEFT))
    elif is_empty(grid, ant, UP):
        move(grid, ant, UP, get_back_pheromone(ant,UP))
    elif is_empty(grid, ant, LEFT):
        move(grid, ant, LEFT, get_back_pheromone(ant,LEFT))
    else:
        print "problem?"
    return 0
    
    
grid = init_grid()

#create_obstacle(grid, BOARD_SIZE[0]/2+6, BOARD_SIZE[0]/2+6, 3, 3)
create_obstacle(grid, 4, 4, 1, 11)
create_obstacle(grid, 6, 2, 2, 2)
create_obstacle(grid, 10, 10, 3, 3)
create_obstacle(grid, 4, 10, 3, 3)
create_obstacle(grid, 4, 4, 3, 3)
create_obstacle(grid, 10, 4, 3, 3)
# 4 walls
create_obstacle(grid, 0, 0, 1, BOARD_SIZE[1])
create_obstacle(grid, 0, 0, BOARD_SIZE[0], 1)
create_obstacle(grid, 0, BOARD_SIZE[1], BOARD_SIZE[0], 1)
create_obstacle(grid, BOARD_SIZE[0], 0, 1, BOARD_SIZE[1])
# creating ants
ant_1 = ant(symbol=ANT_SYMBOL_1, location=STARTING_LOCATION_1)
ant_2 = ant(symbol=ANT_SYMBOL_2, location=STARTING_LOCATION_2)

place_ant_on_grid(grid, ant_1, STARTING_LOCATION_1)
place_ant_on_grid(grid, ant_2, STARTING_LOCATION_2)
print "ant 1 radius:"
print_radius(ant_1)
#print "ant 2 radius:"
#print_radius(ant_2)
print_grid(grid)
for i in range(1,STEPS):
#    print grid[ant.radius[2*RIGHT+1][0],ant.radius[2*RIGHT+1][1]]
    if (step(grid, ant_1) == 1):
        print "MEETING!"
        break
    if (step(grid, ant_2) == 1):
        print "MEETING!"
        break
    print_grid(grid)
else:
    print "NO MEETING!"
#print ant.orientation
#toggle_orientation_clockwise(ant)
#print_radius(ant)
#print ant.orientation
#toggle_orientation_clockwise(ant)
#print_radius(ant)
#print ant.orientation
#toggle_orientation_clockwise(ant)
#print_radius(ant)




#ant = toggle_orientation_clockwise(ant)
#ant = toggle_orientation_clockwise(ant)
#ant = toggle_orientation_clockwise(ant)

#print ant.orientation




