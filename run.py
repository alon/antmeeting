#!/usr/bin/python

#from Final import GOAGrid, GOAAnt
#from MustMeet import COAAnt, COAGrid
import cPickle
import random

import Final
import MustMeet
import antfsm
from render_to_pdf import *

class Run(object):

    # Abstracts

    def make_ants(self, location1, location2):
        raise NotImplemented

    def make_grid(self, board_size):
        raise NotImplemented

    # End Abstracts

    def update_ant_locations(self, ant_locations):
        ants = self.ants
        grid = self.grid
        for i, (ant, location) in enumerate(zip(ants, ant_locations)):
            ant.set_location(location)
            grid.place_ant_on_grid(ant, location)
            #print "ant %s radius:" % (i + 1)
            #ant.print_radius()

    def __init__(self, pyx_output_filename, board_size,
            ant_locations, render_steps = [], draw_slide_title=False):
        # create board, place walls and ants
        self.grid = self.make_grid(board_size=board_size)
        self.board_size = board_size
        self._draw_slide_title = draw_slide_title
        grid = self.grid
        #grid.create_walls()
        ants = self.ants = self.make_ants(ant_locations)
        self.update_ant_locations(ant_locations)
        # initialize pyx variables
        self.pyx_output_filename = pyx_output_filename
        self.render_steps = set(render_steps)

    def single_step(self):
        done = False
        for ant in self.ants:
            if ant is None: continue
            if ant.get_state() != self.FOUND_BASE and self.grid.step(ant) == 1:
                done = True
        return done

    def run(self, steps, renderer=None):
        grid, ants = self.grid, self.ants
        grid.display()
        def pyx_post_step():
            self.canvases = py_renderer.canvases
        post_step = lambda: None
        FOUND_BASE = self.FOUND_BASE
        done = False
        if renderer is None:
            renderer = PyxRenderer(self.pyx_output_filename, draw_slide_title=self._draw_slide_title)
            post_step = pyx_post_step
        for i in range(steps):
            if i in self.render_steps:
                #import pdb; pdb.set_trace()
                grid.display(renderer = renderer, step_num = i)
            done = self.single_step()
            if done:
                break
            grid.display()
            print "step",i
        else:
            print "NO MEETING!"
            i = steps
        #grid.display(pyx_renderer=pyx_renderer, step_num = i)
        grid.display()
        #pyx_renderer.create_pdf() # actually create the output pdf
        post_step()
        return done

class ObstacleRun(Run):

    def set_map(self, grid):
        self.grid.ants = self.ants
        for l_num, l in enumerate(grid):
            for x, c in enumerate(l):
                if self.grid[l_num, x].get_back_arrow() == Final.START:
                    continue
                if c == '*':
                    self.grid[l_num, x].set_obstacle()

    def __init__(self, pyx_output_filename, board_size, ant_locations=[],
        obstacles = [], render_steps=[], draw_slide_title=False):
        obstacles_is_a_map = len(obstacles) > 0 and obstacles[0][0] in ' *'
        if obstacles_is_a_map: # special case, we got a board rep
            ant_locations_d = {}
            for l_num, l in enumerate(obstacles):
                for ant_i, c in enumerate('12'):
                    if l.find(c) != -1:
                        ant_locations_d[ant_i] = l_num + 1, l.find(c) + 1
            if len(ant_locations_d) > 0:
                ant_locations = [ant_locations_d[k] for k in sorted(ant_locations_d.keys())]
            board_size = (len(obstacles[0]), len(obstacles))
        Run.__init__(self, pyx_output_filename, board_size=board_size,
            ant_locations=ant_locations, render_steps=render_steps, draw_slide_title=draw_slide_title)
        grid = self.grid
        if obstacles_is_a_map:
            self.set_map(obstacles)
        else:
            for obst in obstacles:
                grid.create_obstacle(*obst)

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

class GOARun(ObstacleRun):
    FOUND_BASE = Final.FOUND_BASE

    def make_ants(self, ant_locations):
        F = Final
        return [F.GOAAnt(symbol=symbol, location=location, ID=the_id, state=F.NOT_FOUND, bfs=F.SEARCH)
            for location, (symbol, the_id) in zip(ant_locations, [(F.ANT_SYMBOL_1, 1), (F.ANT_SYMBOL_2, 2)])]

    def make_grid(self, board_size):
        return Final.GOAGrid(board_size = board_size)



class COARun(ObstacleRun):
    FOUND_BASE = MustMeet.FOUND_BASE

    def make_grid(self, board_size):
        return MustMeet.COAGrid(board_size = board_size)

    def make_ants(self, ant_locations):
        M = MustMeet
        return [M.COAAnt(symbol=symbol, location=location, ID=the_id, state=M.NOT_FOUND)
            for location, (symbol, the_id) in zip(ant_locations, [(M.ANT_SYMBOL_1, 1), (M.ANT_SYMBOL_2, 2)])]

import antfsm
import constants
from render_to_pdf import render_ant, render_obstacle, render_pheromone

class NOACell(object):
    def __init__(self, row, col, contents):
        self._row = row
        self._col = col
        self._contents = contents
    def get_ant_ID(self):
        return self._contents # '1' or '2' for ants

# UGLY HACK
def juxta(x,y):
    return 11-y,x

class NOAGrid(object):
    def __init__(self, ascii):
        ascii = ascii.split('\n')
        self._grid = [[NOACell(row=row, col=col, contents=ascii[row][col]) for
            col in xrange(len(ascii[0]))] for row in xrange(len(ascii))]
        # Protocol
        self.size = (len(self._grid), len(self._grid[0]))
        self.grid = self

    def get_ant_home(self, i):
        return juxta(*self.ant_homes[i])

    def get_ant_location(self, i):
        return juxta(*self.ant_locations[i])

    def __getitem__(self, row):
        try:
            return self._grid[row[0]][row[1]]
        except:
            return self._grid[row]

    def render_cell(self, cell, c, i, j):
        cmds = []
        x, y = j, self.size[1] - i
        if cell._contents in '12':
            cmds.append(('ant',
                lambda c=c, x=x, y=y: render_ant(c, x, y)))
        elif cell._contents == constants.OBSTACLE:
            cmds.append(('obstacle',
                lambda c=c, x=x, y=y: render_obstacle(c, x, y)))
        elif cell._contents == constants.X:
            cmds.append(('pheromone',
                lambda c=c, x=x, y=y: render_pheromone(c, x, y)))
        return cmds

import copy

class NOARun(object):
    # using alon's old fsm, no use to force it to be the same interface as COA and GOA which are very similar
    def __init__(self, pyx_output_filename, board_size, ant_locations=[],
        obstacles = None, render_steps=[]):
        self.fsm = antfsm.make_meet_fsm(board_size, ant_locations, grid=obstacles)
        self.ant_homes = ant_locations
        self._render_steps = render_steps
        self._pyx_output_filename = pyx_output_filename

    def run(self, steps):
        
        self._renderer = pyx_renderer = PyxRenderer(self._pyx_output_filename)
        for i in range(steps):
            print "NOA %s" % i
            if i in self._render_steps:
                self.record_pdf(i)
            self.fsm.step()
            if self.fsm.getStateRelative(0) == self.fsm.getStateRelative(1):
                print "no change in last state"
                break
        self.record_pdf(i)
        #pyx_renderer.create_pdf() # actually create the output pdf
        self.canvases = pyx_renderer.canvases

    def record_pdf(self, i):
        ascii = self.fsm.asciidump()
        grid = NOAGrid(ascii)
        grid.ant_locations = copy.copy(self.fsm._pos)
        grid.ant_homes = self.ant_homes
        self._renderer.render(grid, title=str(i))

# Runs definition - (constructor, output pdf name, parameters)

defaults = dict(
    board_size = (12,  12), # number of rows (y), number of cols (x)
    ant_locations = [(7, 7), (2, 2)],
    steps = 680
    )

def_board_size = defaults['board_size']

# noa vs coa world

noa_empty_world_1 = """
            
            
            
    1       
            
            
            
            
       2    
            
            
            
""".split("\n")[1:-1] # remove empty lines from start and finish


noa_vs_coa_world = """
            
            
            
     1      
            
     ***    
            
            
       2    
            
            
            
""".split("\n")[1:-1] # remove empty lines from start and finish


# convex world for coa

non_convex_world = """
           *
           *
           *
           *
           *
  *****    *
  *   *    *
  * 1 *    *
  *     2  *
  *****    *
           *
           *
""".split("\n")[1:-1] # remove empty lines from start and finish

infinite_world = """
          * 
          * 
          * 
          * 
          * 
          * 
 *****   2* 
 *   *    * 
 *   *    * 
 *        * 
 *****   1* 
          * 
""".split("\n")[1:-1] # remove empty lines from start and finish

goa_example_world = """
****      * 
*  *      * 
*      **** 
*      *  * 
*    ***2 * 
          * 
 *****    * 
 * 1 *    * 
 *   *    * 
 *        * 
 *****    * 
          * 
""".split("\n")[1:-1] # remove empty lines from start and finish


noa_runs = [
        (NOARun, 'NOA_no_obstacles', dict(
            render_steps = [0, 50]
        )),
        (NOARun, 'NOA_obstacles', dict(
            render_steps = [0, 50],
            obstacles = non_convex_world
        )),
]

coa_runs = [
        (COARun, 'COA_no_obstacles', dict(
            render_steps = [0, 50]
        )),
]

goa_runs = [
        (GOARun, 'GOA_no_obstacles', {}),

        (GOARun, 'GOA_step_by_step', dict(
             obstacles = non_convex_world
            )),
]

noa_meetings = [
        (NOARun, 'NOA_meeting_1', dict(
            ant_locations = [(3,3), (7,7)]
        )),
        (NOARun, 'NOA_meeting_2', dict(
            ant_locations = [(3,5), (7,5)]
        )),
#        (NOARun, 'NOA_meeting_3', dict(
#            ant_locations = [(4,3), (5,7)]
#        )),
]

noa_vs_coa = [
#        (NOARun, 'NOA_vs_COA__NOA', dict(
#            render_steps = [0, 50],
#            obstacles = noa_vs_coa_world
#        )),
        (COARun, 'NOA_vs_COA__COA', dict(
            obstacles = noa_vs_coa_world,
            #render_steps=[26],
            steps = 50
        )),
]

coa_vs_goa = [
        (COARun, 'COA_failure', dict(
            obstacles = non_convex_world,
            steps = 37
        )),
        (COARun, 'COA_infinite', dict(
            obstacles = infinite_world,
            steps = 6
        )),
        (GOARun, 'GOA_success', dict(
            obstacles = non_convex_world
            )),
        (GOARun, 'GOA_example_world', dict(
            obstacles = goa_example_world
            )),
        (GOARun, 'GOA_no_obstacles', dict(
            steps = 120,
            )),
]

goa_steps = [
        (GOARun, 'GOA_no_obstacles', dict(
            steps = 14,
            draw_slide_title = True,
            #render_steps = range(14),
            board_size = (4,  4), # number of rows (y) - 1, number of cols (x) - 1
            ant_locations = [(2, 2)]
            ))
]

slides = [
    #('NOA_meetings', noa_meetings, {}),
    #('NOA_vs_COA', noa_vs_coa, {}),
    #('COA_vs_GOA', coa_vs_goa, {}),

    # Slides used for second version of article:

    #('noa_vs_coa', noa_vs_coa + coa_vs_goa[:2], {'num_in_row':2}),
    #('coa_vs_goa', coa_vs_goa[4:] + coa_vs_goa[2:4], {'num_in_row':2}),
    ('GOA_Steps', goa_steps, {'num_in_row':4, 'with_numbering':False}),
]

def create_pdf_slides(slides):
    STEPS = 680
    for filename, slide, config in slides:
        canvases = []
        for clazz, output_pyx, kw in slide:
            print "using clazz =", clazz
            print "using map =", kw.get('obstacles', 'none')
            the_kw = dict(defaults)
            the_kw.update(kw)
            steps = the_kw['steps']
            del the_kw['steps'] # ugly
            run = clazz(output_pyx, **the_kw)
            run.run(steps)
            canvases.extend(run.canvases)
        print "=========== creating pdf %s from %s frames ===============" % (filename, len(canvases))
        create_pdf(filename, canvases,
            num_in_row = config.get('num_in_row', 5), with_numbering = config.get('with_numbering', True))

def randpoint(size):
    return map(lambda x: random.randint(2, x-3), size)

def randants(run):
    grid = run.grid
    ants = run.ants
    locs = [randpoint(grid.size) for x in xrange(len(ants))]
    def is_obst((x, y)):
        return grid.grid[x][y].is_obstacle()
    while any(map(is_obst, locs)):
        locs = [randpoint(grid.size) for x in xrange(len(ants))]
    run.update_ant_locations(locs)

def multirun():
    from cache import Cacher
    cache = Cacher('runs.sqlite')
    from grid_generators import grid_makers
    grid_makers = grid_makers[:1]
    n = 1
    size = (7, 7)
    params = dict(size=size, p_empty=0.9)
    grids = sum([[f(**params) for x in xrange(n)] for f in grid_makers], [])
    #grids = sum([cache.cached1(f, n, params=params)
    #                             for f in grid_makers], [])
    steps = 5
    output_pyx = 'temp_output.pyx'
    run = GOARun(output_pyx, board_size=size, ant_locations=[(1,1), (3,3)])
    for map in grids:
        run.set_map(map)
        randants(run)
        run.run(steps)

if __name__ == '__main__':
    #create_pdf_slides(slides)
    multirun()

