import time
from base import Grid, Ant
from Ants import (init_grid, create_obstacle, ant, place_ant_on_grid,
    print_radius, print_grid)

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

#from constants import *

class COAAnt(Ant):
    def __init__(self, symbol, location, ID, state):
        self._orientation = UP
        self._symbol = symbol
        self._location = location
        self._ID = ID
        self._state = state
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
    old_location = grid[location] 
    grid[location] = (old_location[0], EMPTY, old_location[2])    
    new_location = radius[2*side + 1]
    ant.set_location(new_location)        
    set_orientation(ant,side)
    if pheromone == EMPTY:
        grid[new_location] = (grid[new_location][0], ANT, grid[new_location][2])
    else:
        grid[new_location] = (pheromone, ANT, symbol)
    
# Backtracking         
def follow_arrow (grid, ant):
    radius = ant.get_radius()
    orientation = ant.get_orientation()
    location = ant.get_location()
    old_location = grid[location]
    grid[location] = (old_location[0], EMPTY, old_location[2])        
    if grid[location][0] == UP_SYM:
#        print "up"
        ant.set_location(radius[(9 - 2*(orientation)) % 8])
        force_orientation(ant,UP)
    elif grid[location][0] == RIGHT_SYM:
#        print "right"
        ant.set_location(radius[(11 - 2*(orientation)) % 8])
        force_orientation(ant,RIGHT)
    elif grid[location][0] == DOWN_SYM:
#        print "down"
        ant.set_location(radius[(13 - 2*(orientation)) % 8])
        force_orientation(ant,DOWN)
    elif grid[location][0] == LEFT_SYM:
#        print "left"
        ant.set_location(radius[(7 - 2*(orientation)) % 8])
        force_orientation(ant,LEFT)
    new_location = ant.get_location()
#    print "new location is ", new_location
    grid[new_location] = (grid[new_location][0], ANT, grid[new_location][2])
#    print ant.orientation
#    time.sleep(2)
            
 
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

def empty(clazz):
    return clazz((EMPTY, EMPTY, EMPTY))

class cell(object):
    def __init__(self, args):
        self._t = tuple(args)
    def get_ant_ID(self):
        return self._t[2]
    def get_back_arrow(self):
        return self._t[0]
    def get_ant_sym(self):
        return self._t[1]
    def __getitem__(self, i):
        return self._t[i]
    def set_obstacle(self):
        self._t = (OBSTACLE, OBSTACLE, OBSTACLE)
    def __str__(self):
        return ''.join(map(str, self._t))

cell.empty = classmethod(empty)


class COAGrid(Grid):

    def __init__(self, board_size):
        Grid.__init__(self, cell = lambda me: cell.empty(), board_size=board_size)

    def __setitem__(self, key, new_item):
        self.grid[key[0]][key[1]] = cell(new_item)

    def create_obstacle(self,x,y,lenx,leny):
        for i in range(y, y+leny):
            for j in range(x, x+lenx):
                self[i,j] = (OBSTACLE,OBSTACLE,OBSTACLE)

    def get_ant_location(self, i):
        return self.ants[i].get_location()

    def get_ant_home(self, i):
        return self.ant_homes[i]

    def place_ant_on_grid(self, ant, location):
        ant_i = int(ant.get_symbol()) - 1
        self[(location)] = (START, ANT, ant.get_symbol())
        self.ant_locations[ant_i] = location
        self.ant_homes[ant_i] = location
        self.ants[ant_i] = ant

    def is_obstacle(self,ant,side):
        radius = ant.get_radius()
        if self[radius[2*side+1][0],radius[2*side+1][1]][0] == OBSTACLE:
            return 1
        return 0
        
    def is_empty(self,ant,side):
        radius = ant.get_radius()
    #    print self[ant.radius[2*side+1][0],ant.radius[2*side+1][1]]
        if self[radius[2*side+1][0],radius[2*side+1][1]][0] == EMPTY:
            return 1
        return 0    

    def dead_end(self, ant):
        if self.is_empty(ant, UP) or self.is_empty(ant, RIGHT) or self.is_empty(ant, LEFT): 
            return 0
        return 1

    def is_ant_in_radius(self, ant):
        radius = ant.get_radius()
        for i in range(0,8):
            if self[radius[i]][1] == ANT:
                return 1
        return 0

    def is_pheromone_in_radius(self, ant):
        radius = ant.get_radius()
        for i in [1,3,5,7]:
            if (self[radius[i]][2] != ant.get_symbol()) and (self[radius[i]][2] != EMPTY) and (self[radius[i]][2] != OBSTACLE):
                return [radius[i],i]
        return 0
        
    def step(self, ant):
        if self.is_ant_in_radius(ant):
            return 1
        ant_pheromone = self.is_pheromone_in_radius(ant)
        
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
        elif ant.get_state() == NOT_FOUND:
            if self.dead_end(ant):
    #        set_orientation(ant, DOWN)
                follow_arrow(self, ant)
            elif self.is_empty(ant, RIGHT):
                move(self, ant, RIGHT, get_back_pheromone(ant,RIGHT))
            elif self.is_obstacle(ant, RIGHT) and self.is_empty(ant, UP):
        #        circle_obstacle(self, ant, RIGHT)
                move(self, ant, UP, get_back_pheromone(ant, UP))
            elif self.is_obstacle(ant, UP):
                move(self, ant, LEFT, get_back_pheromone(ant, LEFT))
            elif self.is_empty(ant, UP):
                move(self, ant, UP, get_back_pheromone(ant,UP))
            elif self.is_empty(ant, LEFT):
                move(self, ant, LEFT, get_back_pheromone(ant,LEFT))
            else:
                print "problem?"
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

def test():
    grid = init_grid()

    #create_obstacle(grid, BOARD_SIZE[0]/2+6, BOARD_SIZE[0]/2+6, 3, 3)
    create_obstacle(grid, 4, 4, 1, 11)
    create_obstacle(grid, 6, 2, 2, 2)
    create_obstacle(grid, 10, 10, 3, 3)
    create_obstacle(grid, 4, 10, 3, 3)
    create_obstacle(grid, 4, 4, 3, 3)
    create_obstacle(grid, 10, 4, 3, 3)
    # 4 walls
    create_obstacle(grid, 0, 1, 1, BOARD_SIZE[0])
    create_obstacle(grid, 0, 0, BOARD_SIZE[1], 1)
    create_obstacle(grid, 1, BOARD_SIZE[0], BOARD_SIZE[1], 1)
    create_obstacle(grid, BOARD_SIZE[1], 0, 1, BOARD_SIZE[0])
    # creating ants
    ant_1 = ant(symbol=ANT_SYMBOL_1, location=STARTING_LOCATION_1, ID=1, state=NOT_FOUND)
    ant_2 = ant(symbol=ANT_SYMBOL_2, location=STARTING_LOCATION_2, ID=2, state=NOT_FOUND)

    place_ant_on_grid(grid, ant_1, STARTING_LOCATION_1)
    place_ant_on_grid(grid, ant_2, STARTING_LOCATION_2)
    print "ant 1 radius:"
    print_radius(ant_1)
    print "ant 2 radius:"
    print_radius(ant_2)
    print_grid(grid)

    for i in range(1,STEPS):
    #    print grid[ant.radius[2*RIGHT+1][0],ant.radius[2*RIGHT+1][1]]
        if (ant_1.get_state() != FOUND_BASE and step(grid, ant_1) == 1):
            print "MEETING!"
            break
        if (ant_2.get_state() != FOUND_BASE and step(grid, ant_2) == 1):
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

if __name__ == '__main__':
    test()

