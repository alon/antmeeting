#from constants import *
import time

from render_to_pdf import *

BOARD_SIZE = (16, 16)
STARTING_LOCATION = (8,8)
STEPS = 70
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
EMPTY = "__"
ANT = "*"
START = "H*"
UP_SYM = "^"
RIGHT_SYM = ">"
DOWN_SYM = "V"
LEFT_SYM = "<"
OBSTACLE = "OO"


class ant(object):
    orientation = UP
    location = STARTING_LOCATION        
    #123
    #804
    #765
    radius = [(location[0]-1,location[1]-1),
              (location[0]-1,location[1]),
              (location[0]-1,location[1]+1),
              (location[0],location[1]+1),
              (location[0]+1,location[1]+1),
              (location[0]+1,location[1]),
              (location[0]+1,location[1]-1),
              (location[0],location[1]-1)
              ]
    
    
def init_grid():
    grid = {}
    for i in range(0, BOARD_SIZE[0]+1):
        for j in range(0, BOARD_SIZE[1]+1):
            grid[i,j] = EMPTY
    return grid
    
def place_ant_on_grid(grid, ant):
    grid[(ant.location)] = START    
     
def ant_update_radius(ant):
    ant.radius[0 - 2*ant.orientation % 8] = (ant.location[0]-1,ant.location[1]-1)
    ant.radius[1 - 2*ant.orientation % 8] = (ant.location[0]-1,ant.location[1])
    ant.radius[2 - 2*ant.orientation % 8] = (ant.location[0]-1,ant.location[1]+1)
    ant.radius[3 - 2*ant.orientation % 8] = (ant.location[0],ant.location[1]+1)
    ant.radius[4 - 2*ant.orientation % 8] = (ant.location[0]+1,ant.location[1]+1)
    ant.radius[5 - 2*ant.orientation % 8] = (ant.location[0]+1,ant.location[1])
    ant.radius[6 - 2*ant.orientation % 8] = (ant.location[0]+1,ant.location[1]-1)
    ant.radius[7 - 2*ant.orientation % 8] = (ant.location[0],ant.location[1]-1)
    

def print_radius(ant):
    print ant.radius[0],ant.radius[1],ant.radius[2]
    print ant.radius[7],ant.location,ant.radius[3]
    print ant.radius[6],ant.radius[5],ant.radius[4]
    print " "
    
def toggle_orientation_clockwise(ant):
    ant.orientation = (ant.orientation + 1) % 4
    ant_update_radius(ant)
    
def set_orientation(ant,side):
    ant.orientation = (ant.orientation + side) % 4
    ant_update_radius(ant)

def force_orientation(ant,side):
    ant.orientation = side
    ant_update_radius(ant)


class AntsPyxRenderer(PyxRenderer):
    def render_cell(self, the_cell, c, i, j):
        """ draw cell onto canvas """
        symb = the_cell[0]
        if symb not in [UP_SYM, DOWN_SYM, LEFT_SYM, RIGHT_SYM]:
            return
        dx, dy = {UP_SYM: (0, -1), DOWN_SYM: (0, 1), LEFT_SYM: (-1, 0), RIGHT_SYM: (1, 0)}[symb]
        c.stroke(path.line(j, self.max_y - i, j + dx, self.max_y - (i + dy)), [deco.earrow()])

pyx_renderer = AntsPyxRenderer()

def print_grid(grid):
    pyx_renderer.render(grid, BOARD_SIZE)
    for i in range(0, BOARD_SIZE[0]+1):
        for j in range(0, BOARD_SIZE[1]+1):
            print grid[i,j],
        print " "
    print " "
 
def move(grid, ant, side, pheromone):
    grid[ant.location] = grid[ant.location].replace(ANT,"_")
    ant.location = ant.radius[2*side + 1]        
    set_orientation(ant,side)
    grid[ant.location] = pheromone
    grid[ant.location] += ANT
#    print_radius(ant)
        
def follow_arrow (grid, ant):
    grid[ant.location] = grid[ant.location].replace(ANT,"_")        
    if grid[ant.location].find(UP_SYM) > -1:
#        print "up"
        ant.location = ant.radius[(9 - 2*(ant.orientation)) % 8]
        force_orientation(ant,UP)
    elif grid[ant.location].find(RIGHT_SYM) > -1:
#        print "right"
        ant.location = ant.radius[(11 - 2*(ant.orientation)) % 8]
        force_orientation(ant,RIGHT)
    elif grid[ant.location].find(DOWN_SYM) > -1:
#        print "down"
        ant.location = ant.radius[(13 - 2*(ant.orientation)) % 8]
        force_orientation(ant,DOWN)
    elif grid[ant.location].find(LEFT_SYM) > -1:
#        print "left"
        ant.location = ant.radius[7 - 2*(ant.orientation)]
        force_orientation(ant,LEFT)
    grid[ant.location] = grid[ant.location].replace("_",ANT)
#    print ant.orientation
#    time.sleep(2)
            
def create_obstacle(grid,x,y,lenx,leny):
    for i in range(y, y+leny):
        for j in range(x, x+lenx):
            grid[i,j] = OBSTACLE
    
def get_back_pheromone(ant,move):
    if (ant.orientation + move) % 4 == 0:
        return DOWN_SYM
    elif (ant.orientation + move) % 4 == 1:
        return LEFT_SYM
    elif (ant.orientation + move) % 4 == 2:
        return UP_SYM
    elif (ant.orientation + move) % 4 == 3:
        return RIGHT_SYM           
#def is_pheromone_right(grid,ant):

def circle_obstacle(grid, ant, side):    
    while is_obstacle(grid, ant, side) and is_empty(grid, ant, (side - 1 % 4)):
        move(grid, ant, (side - 1 % 4), get_back_pheromone(ant, (side - 1 % 4)))    

def is_obstacle(grid,ant,side):
    if grid[ant.radius[2*side+1][0],ant.radius[2*side+1][1]] == OBSTACLE:
        return 1
    return 0
    
def is_empty(grid,ant,side):
    if grid[ant.radius[2*side+1][0],ant.radius[2*side+1][1]] == EMPTY:
        return 1
    return 0    

def dead_end(grid, ant):
    if is_empty(grid, ant, UP) or is_empty(grid, ant, RIGHT) or is_empty(grid, ant, LEFT): 
        return 0
    return 1

grid = init_grid()
#create_obstacle(grid, BOARD_SIZE[0]/2+6, BOARD_SIZE[0]/2+6, 3, 3)

#create_obstacle(grid, 4, 4, 1, 12)
#create_obstacle(grid, 6, 2, 2, 2)
#create_obstacle(grid, 10, 10, 3, 3)
#create_obstacle(grid, 4, 10, 3, 3)
#create_obstacle(grid, 4, 4, 3, 3)
#create_obstacle(grid, 10, 4, 3, 3)
place_ant_on_grid(grid, ant)
print_radius(ant)

for i in range(1,STEPS):
#    print grid[ant.radius[2*RIGHT+1][0],ant.radius[2*RIGHT+1][1]]
    print_grid(grid)
    if is_empty(grid, ant, RIGHT):
        move(grid, ant, RIGHT, get_back_pheromone(ant,RIGHT))
    elif is_obstacle(grid, ant, RIGHT) and is_empty(grid, ant, UP):
#        circle_obstacle(grid, ant, RIGHT)
        move(grid, ant, UP, get_back_pheromone(ant, UP))
    elif is_obstacle(grid, ant, UP):
        circle_obstacle(grid, ant, UP)
    elif is_empty(grid, ant, UP):
        move(grid, ant, UP, get_back_pheromone(ant,UP))
    elif is_empty(grid, ant, LEFT):
        move(grid, ant, LEFT, get_back_pheromone(ant,LEFT))
    else:
#        set_orientation(ant, DOWN)
#        print ant.orientation 
        while dead_end(grid, ant):
            follow_arrow(grid, ant)
            print_grid(grid)
        

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

print_grid(grid)


