#!/usr/bin/env python

import AStar
import run 
import maps

N=20 # limit screen size
print "using N=%s" % N
maze = 'maze_000.map'
random_homes_pair = maps.random_homes_pair_gen(N,maze)
random_map_pair = maps.random_map_pair_gen(N,0.7)

test_pair = (
    lambda : ['     ',' *** ', ' *** ', ' *** ', '     '],
    lambda defaults, size: [(1, 0), (4, 3)]
)

def xys(width, height):
    return zip(range(width)*height, sum([[i]*width for i in range(height)],[]))

snart = {-1:'*', 1:' '}

def pos(homes, mapdata, x, y):
   return (str(homes.index((x,y)) + 1)
           if (x,y) in homes else snart[mapdata[(x,y)]])

def astar(homes, zmap):
    startpoint, endpoint = homes = map(tuple, homes)
    width, height = len(zmap), len(zmap[0])
    trans = {'*':-1, ' ':1}
    mapdata = dict([((x,y),trans[zmap[x][y]]) for x,y in xys(width, height)])
    for x in range(width):
        print ''.join(pos(homes,mapdata,x,y) for y in range(height))
    astar = AStar.AStar(AStar.SQ_MapHandler(mapdata, width, height))
    start = AStar.SQ_Location(startpoint[0],startpoint[1])
    end = AStar.SQ_Location(endpoint[0],endpoint[1])
    p = astar.findPath(start,end)
    if p:
        return len(p.nodes)
    else:
        return None

def randomize():
    make_map, make_homes = random_map_pair
    zmap, homes = maps.make_map_with_ants_on_vacancies(
        default_homes=[(2,2), (3,7)],
        make_map=make_map, make_homes=make_homes)
    return zmap, homes

def generate_data():
    for i in xrange(10):
        yield randomize()

class Data(object):
    pass
        
def main():
    f = open('testResults.txt', 'w')
    f.write("Shortest path, Number of steps, Number of pheromones\n") 
    for the_map, homes in generate_data():
        s = Data()
        s.board_size = (len(the_map), len(the_map[0]))
        s.homes = homes
        goa=run.GOARun('', board_size=s.board_size, ant_locations=s.homes)
        #goa.grid.display()
        goa.set_map(the_map)
        #goa.grid.display()
        done = False
        s.steps = 0
        shortest = astar(homes, the_map)
        print "shortest path", shortest
        if shortest is None:
            break
        i=0        
        while 1:
            done, num_of_pheromones = goa.single_step()
            if done:
                s = '%s, %s, %s\n' % (shortest, i, num_of_pheromones)
                f.write(s)
        
                print "num of steps",i
                print "num of pheromones", num_of_pheromones
                break
            i+=1
        # calculate measureables
        # measurable A
        # measurable B
        # record in db (file/sqlite)
    f.close()
    # create report

if __name__ == '__main__':
    main()
