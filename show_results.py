import sqlite3
import cPickle

def c_or_num(x, y, c, homes):
    for ant_i, (ant_x, ant_y) in enumerate(homes):
        if ant_x == x and ant_y == y:
            return str(ant_i+1)
    return c

def line_with_homes(y, line, homes):
    return ''.join(c_or_num(x, y, c, homes) for x, c in enumerate(line))

def map_with_homes(zmap, homes):
    return [line_with_homes(y, line, homes) for y, line in enumerate(zmap)]

def show_all_results():
    con = sqlite3.connect('ant_results.sqlite3')
    c = con.cursor()
    all_results = [map(lambda u: cPickle.loads(str(u)), x) for x in c.execute('select * from results').fetchall()]
    print '\n'.join('%s\nresults: %s' % (
        '\n'.join(map_with_homes(zmap, homes)), results)
        for (zmap, homes), results in all_results)

def get_unfinished():
    con = sqlite3.connect('ant_results.sqlite3')
    c = con.cursor()
    finished = [cPickle.loads(str(u[0])) for u in c.execute('select params from results ').fetchall()]
    with open('maps_homes.pickle') as fd:
        maps_homes = cPickle.load(fd)
    for map_homes in maps_homes:
        if map_homes not in finished:
            print "unfinshed:\n%s" % '\n'.join(map_with_homes(*map_homes))
            return map_homes
    return None

if __name__ == '__main__':
    show_all_results()
