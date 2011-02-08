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

con = sqlite3.connect('ant_results.sqlite3')
c = con.cursor()
all_results = [map(lambda u: cPickle.loads(str(u)), x) for x in c.execute('select * from results').fetchall()]
print '\n'.join('%s\nresults: %s' % (
    '\n'.join(map_with_homes(zmap, homes)), results)
    for (zmap, homes), results in all_results)

