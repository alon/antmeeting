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

test_pair = (
    lambda : ['     ',' *** ', ' *** ', ' *** ', '     '],
    lambda defaults, size: [(1, 0), (4, 3)]
)

def test_pygame(default_homes = [(2,2), (3,7)]):
    #make_map, make_homes = random_map_pair
    make_map, make_homes = random_homes_pair
    #make_map, make_homes = test_pair
    class Data(object):
        pass
    s = Data()
    s.steps = 0
    cont = True
    renderer = PyGameRenderer()
    s.num = 0
    action = lambda x, y: x + y
    def next_step(k):
        s.steps += 1
    def prev_step(k):
        s.steps = max(0, s.steps - 1)
    def randomize(k):
        s.zmap, s.homes = make_map_with_ants_on_vacancies(
            default_homes=default_homes,
            make_map=make_map, make_homes=make_homes)
        s.board_size = (len(s.zmap), len(s.zmap[0]))
    randomize(None)
    keys = {'a': next_step, 'z': prev_step,
            'r': randomize}
    while cont:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == KEYDOWN and event.unicode == 'q':
                cont = False
            elif event.type == KEYDOWN:
                if event.unicode in keys.keys():
                    keys[event.unicode](event.unicode)
                elif ord('0') <= event.key <= ord('9'):
                    s.num = s.num*10 + event.key - ord('0')
                elif event.unicode == '-':
                    action = lambda x, y: x - y
                elif event.key == 13:
                    s.steps = max(0, action(s.steps, s.num))
                    s.num = 0
                    action = lambda x, y: x + y
                elif event.unicode == 'p':
                    import pdb; pdb.set_trace()
            pygame.display.set_caption(str(s.steps))
        if cont:
            goa=run.GOARun('', board_size=s.board_size, ant_locations=s.homes)
            #goa.grid.display()
            goa.set_map(s.zmap)
            #goa.grid.display()
            done = False
            for i in xrange(s.steps):
                done = goa.single_step()
                if done:
                    done_step = i
                    break
            if done:
                pygame.display.set_caption('MEETING - %d (%d)' % (done_step, s.steps))
            renderer.render(goa.grid, 1)
            pygame.time.delay(10)

if __name__ == '__main__':
    test_pygame()

