#!/usr/bin/python

import random
import run
import pygame
from pygame import KEYDOWN
import grid_generators
import maps
from render import PyGameRenderer

def chunk(n, ll):
    return [l[:n] for l in ll[:n]]

random_map_pair = (
    lambda: grid_generators.grid_makers[0](size=(10,10), p_empty=0.9)
    ,lambda defaults, size: defaults
)
random_homes_pair = (
    lambda: chunk(10, maps.read_maze('maze_000.map'))
    ,lambda defaults, size: [map(lambda s: random.randint(0, s-1), size) for i in xrange(len(defaults))]
)

def make_map_with_ants_on_vacancies(default_homes, make_map, make_homes):
    zmap = make_map()
    size = (len(zmap), len(zmap[0]))
    homes = make_homes(defaults=default_homes, size=size)
    while any([zmap[x][y] == '*' for x, y in homes]):
        print "."
        zmap = make_map()
        homes = make_homes(defaults=default_homes, size=size)
    return zmap, homes

def test_pygame(default_homes = [(2,2), (3,7)]):
    #make_map, make_homes = random_map_pair
    make_map, make_homes = random_homes_pair
    zmap, homes = make_map_with_ants_on_vacancies(
        default_homes=default_homes,
        make_map=make_map, make_homes=make_homes)
    board_size = (len(zmap), len(zmap[0]))
    steps = 1
    cont = True
    renderer = PyGameRenderer()
    num = 0
    action = lambda x, y: x + y
    while cont:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == KEYDOWN and event.unicode == 'q':
                cont = False
            elif event.type == KEYDOWN:
                if event.unicode == 'a':
                    steps += 1
                elif event.unicode == 'z':
                    steps = max(0, steps - 1)
                elif ord('0') <= event.key <= ord('9'):
                    num = num*10 + event.key - ord('0')
                elif event.unicode == '-':
                    action = lambda x, y: x - y
                elif event.key == 13:
                    steps = max(0, action(steps, num))
                    num = 0
                    action = lambda x, y: x + y
                elif event.unicode == 'p':
                    import pdb; pdb.set_trace()
            pygame.display.set_caption(str(steps))
        if cont:
            goa=run.GOARun('', board_size=board_size, ant_locations=homes)
            #goa.grid.display()
            goa.set_map(zmap)
            #goa.grid.display()
            done = False
            for i in xrange(steps):
                done = goa.single_step()
                if done:
                    done_step = i
                    break
            if done:
                pygame.display.set_caption('MEETING - %d (%d)' % (done_step, steps))
            renderer.render(goa.grid, 1)
            pygame.time.delay(10)

if __name__ == '__main__':
    test_pygame()

