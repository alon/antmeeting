#!/usr/bin/python

import random
import run
import pygame
from pygame import KEYDOWN
import grid_generators
import maps
from render import PyGameRenderer
import show_results
from maps import (random_homes_pair_gen, random_map_pair_gen,
     make_map_with_ants_on_vacancies)

def test_pygame(default_homes = [(2,2), (3,7)]):
    #make_map, make_homes = random_map_pair
    #make_map, make_homes = random_homes_pair_gen(10)
    make_map, make_homes = random_map_pair_gen(10,0.9)
    #make_map, make_homes = test_pair
    class Data(object):
        pass
    s = Data()
    s.steps = 0
    cont = True
    renderer = PyGameRenderer()
    s.num = 0
    s.cont = True
    s.action = lambda x, y: x + y
    def next_step(k):
        s.steps += 1
    def prev_step(k):
        s.steps = max(0, s.steps - 1)
    def randomize(k):
        s.zmap, s.homes = make_map_with_ants_on_vacancies(
            default_homes=default_homes,
            make_map=make_map, make_homes=make_homes)
        s.board_size = (len(s.zmap), len(s.zmap[0]))
    def astar(k):
        import AStar
        startpoint, endpoint = homes = map(tuple, s.homes)
        width, height = s.board_size
        trans = {'*':-1, ' ':1}
        snart = {-1:'*', 1:' '}
        mapdata = dict([((x,y),trans[s.zmap[x][y]]) for x,y in xys(width, height)])
        def pos(mapdata, x, y):
            if (x,y) in homes:
                return str(homes.index((x,y)) + 1)
            return snart[mapdata[(x,y)]]
        for x in range(width):
            print ''.join(pos(mapdata,x,y) for y in range(height))
        astar = AStar.AStar(AStar.SQ_MapHandler(mapdata, width, height))
        start = AStar.SQ_Location(startpoint[0],startpoint[1])
        end = AStar.SQ_Location(endpoint[0],endpoint[1])
        p = astar.findPath(start,end)
        if p:
            print p, len(p.nodes)
        else:
            print "no path"

    unfinished = show_results.get_unfinished()
    if unfinished:
        s.zmap, s.homes = unfinished
        s.board_size = (len(s.zmap), len(s.zmap[0]))
    else:
        randomize(None)
    keys = {'a': next_step, 'z': prev_step,
            'r': randomize, 's': astar}
    def singlestep():
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == KEYDOWN and event.unicode == 'q':
                s.cont = False
            elif event.type == KEYDOWN:
                if event.unicode in keys.keys():
                    keys[event.unicode](event.unicode)
                elif ord('0') <= event.key <= ord('9'):
                    s.num = s.num*10 + event.key - ord('0')
                elif event.unicode == '-':
                    s.action = lambda x, y: x - y
                elif event.key == 13:
                    s.steps = max(0, s.action(s.steps, s.num))
                    s.num = 0
                    s.action = lambda x, y: x + y
                elif event.unicode == 'p':
                    import pdb; pdb.set_trace()
            pygame.display.set_caption(str(s.steps))
        if s.cont:
            #goa=run.GOARun('', board_size=s.board_size, ant_locations=s.homes)
            coa=run.COARun(pyx_output_filename='', board_size=s.board_size, ant_locations=s.homes, number_of_active_ants=1)
            #goa.grid.display()
            #goa.set_map(s.zmap)
            coa.set_map(s.zmap)
            #goa.grid.display()
            done = False
            for i in xrange(s.steps):
                #done, number_of_phers = goa.single_step()
                done, number_of_phers = coa.single_step()
                if done:
                    done_step = i
                    break
            if done:
                pygame.display.set_caption('MEETING - %d (%d)' % (done_step, s.steps))
            #renderer.render(goa.grid, 1)
            renderer.render(coa.grid, 1)
            pygame.time.delay(10)

    while s.cont:
        try:
            singlestep()
        except KeyboardInterrupt:
            s.cont = False
    print "pygame exit time sucks"

if __name__ == '__main__':
    test_pygame()

