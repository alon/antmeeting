import time
from base import Grid, Ant
from pyx import *

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

class cell(object):
    def __init__(self, *args):
        self._t = tuple(*args)
    @classmethod
    def empty(clazz):
        return clazz((EMPTY, EMPTY, EMPTY))
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

class COAGrid(Grid):

    def __init__(self, board_size):
        Grid.__init__(self, cell = lambda me: cell.empty(), board_size=board_size)

    def __setitem__(self, key, new_item):
        self.grid[key[0]][key[1]] = cell(new_item)

    def create_obstacle(grid,x,y,lenx,leny):
        for i in range(y, y+leny):
            for j in range(x, x+lenx):
                grid[i,j] = (OBSTACLE,OBSTACLE,OBSTACLE)

    def get_ant_location(self, i):
        return self.ants[i].get_location()

    def get_ant_home(self, i):
        return self.ant_homes[i]

    def place_ant_on_grid(grid, ant, location):
        ant_i = int(ant.get_symbol()) - 1
        grid[(location)] = (START, ANT, ant.get_symbol())
        grid.ant_locations[ant_i] = location
        grid.ant_homes[ant_i] = location
        grid.ants[ant_i] = ant

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
        if grid.is_empty(ant, UP) or grid.is_empty(ant, RIGHT) or grid.is_empty(ant, LEFT): 
            return 0
        return 1

    def is_ant_in_radius(grid, ant):
        radius = ant.get_radius()
        for i in range(0,8):
            if grid[radius[i]][1] == ANT:
                return 1
        return 0

    def is_pheromone_in_radius(grid, ant):
        radius = ant.get_radius()
        for i in [1,3,5,7]:
            if (grid[radius[i]][2] != ant.get_symbol()) and (grid[radius[i]][2] != EMPTY) and (grid[radius[i]][2] != OBSTACLE):
                return [radius[i],i]
        return 0
        
    def step(grid, ant):
        if grid.is_ant_in_radius(ant):
            return 1
        ant_pheromone = grid.is_pheromone_in_radius(ant)
        
        if ant.get_state() == NOT_FOUND and ant_pheromone != 0:
    #        print "ant pheromone", ant_pheromone        
            if ant.get_ID() > int(grid[ant_pheromone[0]][2]):
    #            print "master"
                ant.set_state(FOUND_PHEROMONE_MASTER)
                side = (ant_pheromone[1]-1)/2
    #            print side
                move(grid, ant, side, EMPTY)
            else:
    #            print "servant"
                ant.set_state(FOUND_PHEROMONE_SERVANT)
                follow_arrow(grid, ant)        
        elif ant.get_state() == NOT_FOUND:
            if grid.dead_end(ant):
    #        set_orientation(ant, DOWN)
                follow_arrow(grid, ant)
            elif grid.is_empty(ant, RIGHT):
                move(grid, ant, RIGHT, get_back_pheromone(ant,RIGHT))
            elif grid.is_obstacle(ant, RIGHT) and grid.is_empty(ant, UP):
        #        circle_obstacle(grid, ant, RIGHT)
                move(grid, ant, UP, get_back_pheromone(ant, UP))
            elif grid.is_obstacle(ant, UP):
                move(grid, ant, LEFT, get_back_pheromone(ant, LEFT))
            elif grid.is_empty(ant, UP):
                move(grid, ant, UP, get_back_pheromone(ant,UP))
            elif grid.is_empty(ant, LEFT):
                move(grid, ant, LEFT, get_back_pheromone(ant,LEFT))
            else:
                print "problem?"
        elif ant.get_state() == FOUND_PHEROMONE_MASTER:
            location = ant.get_location()
            if grid[location][0] == "H":
                ant.set_state(FOUND_BASE)
            else:
                follow_arrow(grid, ant)
            #follow trail to other base
        elif ant.get_state() == FOUND_PHEROMONE_SERVANT:
            follow_arrow(grid, ant)
    #        print "following"
            #follow trail to base
        return 0

    def render_cell(self, cell, c, i, j):
        """ draw cell onto canvas """
        BOARD_SIZE = self.size
        # note that x and y are inverted, and that we put max_y - y to flip y
        x, y = j, BOARD_SIZE[0] - i
        grey = color.rgb(0.5,0.5,0.5)
        back_arrow = cell.get_back_arrow()
        cmds = []
        if cell.get_ant_sym() == ANT:
            from render_to_pdf import render_ant
            # render the ant
            cmds.append(('ant',
                lambda c=c, x=x, y=y: render_ant(c, x, y)))
        if back_arrow == START: # draw H
            #c.text(j, BOARD_SIZE[1] - i, 'H')
            cmds.append(('home',
                lambda self=self, c=c, i=i, j=j: self.draw_home(
                    c, i, j)))
        elif back_arrow == OBSTACLE:
            assert(cell.get_ant_sym() == back_arrow)
            cmds.append(('obstacle',
                lambda c=c, x=x, y=y: c.fill(
                    path.rect(x - 0.25, y - 0.25, 0.5, 0.5))))
        else:
            back_arrow = cell.get_back_arrow()
            if back_arrow in [UP_SYM, DOWN_SYM, LEFT_SYM, RIGHT_SYM]:
                dx, dy = {UP_SYM: (0, -1), DOWN_SYM: (0, 1), LEFT_SYM: (-1, 0), RIGHT_SYM: (1, 0)}[back_arrow]
                cmds.append(('arrow',
                    lambda c=c, x=x, y=y, dx=dx, dy=dy: c.stroke(
                    path.line(x, y, x + dx, y - dy), [deco.earrow(),
                        style.linewidth(0.05)])))
        return cmds


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

