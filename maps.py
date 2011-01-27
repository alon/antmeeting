# TODO: linecache is not in shedskin
#import linecache

import random
import my_linecache as linecache
import grid_generators
            
def read_maze(fname):
    trans = dict(zip('.@', ' *'))
    lines = [''.join([trans.get(x, x) for x in l.strip()]) for l in linecache.getlines(fname)]
    map_type, height, width = lines[0], int(lines[1].strip().split()[1]), int(lines[2].strip().split()[1])
    assert(lines[3].strip() == 'map')
    assert(len(lines[4:]) == height)
    rows = lines[4:]
    assert(all(map(lambda x: len(x) == width, rows)))
    return rows

def make_map_with_ants_on_vacancies(default_homes, make_map, make_homes):
    zmap = make_map()
    size = (len(zmap), len(zmap[0]))
    homes = make_homes(defaults=default_homes, size=size)
    while any([zmap[x][y] == '*' for x, y in homes]):
        print "."
        zmap = make_map()
        homes = make_homes(defaults=default_homes, size=size)
    return zmap, homes

def chunk(n, ll):
    return [l[:n] for l in ll[:n]]


def random_homes(defaults, size):
    return [map(lambda s: random.randint(0, s-1), size) for i in xrange(len(defaults))]

random_maze_map_pair = (
    lambda: grid_generators.maze_by_iterative_partition(size=(10,10), p_empty=0.9)
    ,random_homes
)

def random_map_pair_gen(N, p_empty):
    return (
        lambda: grid_generators.grid_makers[0](size=(N,N), p_empty=p_empty)
        ,random_homes
    )

    
def random_homes_pair_gen(N,maze):
    return (
        lambda: chunk(N, read_maze(maze)),
        random_homes
    )
