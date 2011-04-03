import sqlite3
import cPickle
import csv
import sys

def c_or_num(x, y, c, homes):
    for ant_i, (ant_x, ant_y) in enumerate(homes):
        if ant_x == x and ant_y == y:
            return str(ant_i+1)
    return c

def line_with_homes(y, line, homes):
    return ''.join(c_or_num(x, y, c, homes) for x, c in enumerate(line))

def map_with_homes(zmap, homes):
    return [line_with_homes(y, line, homes) for y, line in enumerate(zmap)]

def show_all_results(show_map=False):
    con = sqlite3.connect('ant_results.sqlite3')
    c = con.cursor()
    all_results = [map(lambda u: cPickle.loads(str(u)), x) for x in c.execute('select * from results').fetchall()]
    render_map = lambda zmap, homes: ''
    writer = csv.writer(sys.stdout)
    if show_map:
        render_map = lambda zmap, homes: '\n'.join(map_with_homes(zmap, homes))
    rows = [[render_map(zmap, homes)] + results[:1] + sum(map(list, results[1:]), [])
        for (zmap, homes), results in all_results]
    writer.writerows(rows)

def get_unfinished():
    con = sqlite3.connect('ant_results.sqlite3')
    c = con.cursor()
    def maph_to_key(m):
        return tuple(map(lambda x: tuple(map(tuple, x)), m))
    finished = [(cPickle.loads(str(u[0])), cPickle.loads(str(u[1]))) for u in c.execute('select * from results ').fetchall()]
    finished = [(maph_to_key(u[0]), tuple(u[1])) for u in finished]
    f_d = dict(finished)
    with open('maps_homes.pickle') as fd:
        maps_homes = cPickle.load(fd)
    for map_homes in maps_homes:
        map_homes = maph_to_key(map_homes)
        if (None,None) in f_d[map_homes]:
            print "unfinshed:\n%s" % '\n'.join(map_with_homes(*map_homes))
            return map_homes
    return None

if __name__ == '__main__':
    show_all_results()
