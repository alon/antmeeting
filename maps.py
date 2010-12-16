# TODO: linecache is not in shedskin
#import linecache

import my_linecache as linecache

def read_maze(fname):
    trans = dict(zip('.@', ' *'))
    lines = [''.join([trans.get(x, x) for x in l.strip()]) for l in linecache.getlines(fname)]
    map_type, height, width = lines[0], int(lines[1].strip().split()[1]), int(lines[2].strip().split()[1])
    assert(lines[3].strip() == 'map')
    assert(len(lines[4:]) == height)
    rows = lines[4:]
    assert(all(map(lambda x: len(x) == width, rows)))
    return rows

