#!/usr/bin/python

import Final
import MustMeet

class Run(object):

    # Abstracts

    def make_ants(self, location1, location2):
        raise NotImplemented

    def make_grid(self, board_size):
        raise NotImplemented

    # End Abstracts

    def __init__(self, board_size, ant_locations, number_of_active_ants=2,
                 render_steps = [], draw_slide_title=False, pyx_output_filename=''):
        # create board, place walls and ants
        self.grid = self.make_grid(board_size=board_size)
        self.board_size = board_size
        self._draw_slide_title = draw_slide_title
        grid = self.grid
        ants = self.ants = self.make_ants(ant_locations)
        self.update_ant_locations(ant_locations)
        # initialize pyx variables
        self.pyx_output_filename = pyx_output_filename
        self.render_steps = set(render_steps)
        self.number_of_active_ants = number_of_active_ants

    def update_ant_locations(self, ant_locations):
        ants = self.ants
        grid = self.grid
        for i, (ant, location) in enumerate(zip(ants, ant_locations)):
            ant.set_location(tuple(location))
            grid.place_ant_on_grid(ant, tuple(location))
            #print "ant %s radius:" % (i + 1)
            #ant.print_radius()

    def single_step(self):
        num_of_pheromones = 0
        done = False
        for ant in self.ants:
            if self.number_of_active_ants == 1 and ant != number_of_active_ants:
                continue
            if ant is None: continue
            if ant.get_state() != self.FOUND_BASE and self.grid.step(ant) == 1:
                done = True
                num_of_pheromones = ant.get_num_of_pheromones()
        return done, num_of_pheromones

    def run(self, steps, renderer=None, post_step = lambda: None):
        grid, ants = self.grid, self.ants
        grid.display()
        FOUND_BASE = self.FOUND_BASE
        done = False
        for i in range(steps):
            if i in self.render_steps:
                #import pdb; pdb.set_trace()
                if renderer:
                    renderer.render(grid, title=str(i))
                grid.display(step_num = i)
            done = self.single_step()
            if done:
                break
            grid.display()
            print "step",i
        else:
            print "NO MEETING!"
            i = steps
        grid.display()
        post_step()
        return done

class ObstacleRun(Run):

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
            for x, y, lenx, leny in obstacles:
                grid.create_obstacle(x, y, lenx, leny)

    def set_map(self, grid):
        self.grid.ants = self.ants
        for l_num, l in enumerate(grid):
            for x, c in enumerate(l):
                if self.grid.get((l_num, x)).get_back_arrow() == Final.START:
                    continue
                if c == '*':
                    self.grid.get((l_num, x)).set_obstacle()


class GOARun(ObstacleRun):
    FOUND_BASE = Final.FOUND_BASE

    def __init__(self, board_size, number_of_active_ants, ant_locations=[],
        obstacles = [], render_steps=[], draw_slide_title=False, pyx_output_filename=''):
        super(GOARun, self).__init__(board_size, number_of_active_ants,
            ant_locations, obstacles, render_steps, draw_slide_title, pyx_output_filename)

    def make_ants(self, ant_locations):
        return Final.make_ants(tuple(map(tuple,ant_locations)))

    def make_grid(self, board_size):
        return Final.make_grid(list(board_size))

class COARun(ObstacleRun):
    FOUND_BASE = MustMeet.FOUND_BASE

    def __init__(self, board_size, number_of_active_ants, ant_locations=[],
        obstacles = [], render_steps=[], draw_slide_title=False, pyx_output_filename=''):
        super(COARun, self).__init__(board_size, number_of_active_ants,
            ant_locations, obstacles, render_steps, draw_slide_title, pyx_output_filename)

    def make_ants(self, ant_locations):
        return MustMeet.make_ants(tuple(map(tuple,ant_locations)))

    def make_grid(self, board_size):
        return MustMeet.make_grid(list(board_size))

        
if False:
    the_map = [[0]*n for i in xrange(10)]
    homes=[(2,2), (3,7)],
    board_size = (len(the_map), len(the_map[0]))
    goa=GOARun('', board_size=board_size, ant_locations=homes)
    goa.set_map(the_map)
    done, num_of_pheromones = goa.single_step()
