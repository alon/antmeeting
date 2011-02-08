#!/usr/bin/env python

import AStar
import run 
import maps
import sqlite3
import os
import cPickle

#random_homes_pair = maps.random_homes_pair_gen(N,maze)
#random_map_pair = maps.random_map_pair_gen(N,0.7)

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
    """ generate pairs of (map, homes) """
    N=20 # limit screen size
    print "using N=%s" % N
    mazes = [maps.read_maze('maze_%03d.map' % i) for i in xrange(5)]
    for maze in mazes: #5 mazes, 5 10% map, 5 20% map, 5 30% map
       for i in xrange(100):
           zmap, homes = maps.make_map_with_ants_on_vacancies(
                default_homes=[(2,2), (3,7)],
                make_map=lambda maze=maze: maze, make_homes=maps.random_homes)
           yield zmap, homes
           #astar, ROA, ROA one ant, GOA, GOA one ant
           #    time, num of pheromones

class Data(object):
    pass

def single_run(the_map, homes):
    a = [astar(homes, the_map)]
    a.extend([single_run_alg(run_func, the_map, homes) for run_func in [run.GOARun, run.COARun]])
    a.extend([single_run_alg_one_ant(run_func, the_map, homes) for run_func in [run.GOARun, run.COARun]])
    return a

def single_run_alg_one_ant(run_func, the_map, homes):
    single_run_alg(run_func, the_map, homes, number_of_active_ants=1)

def single_run_alg(run_func, the_map, homes, number_of_active_ants=2):
    s = Data()
    s.board_size = (len(the_map), len(the_map[0]))
    s.homes = homes
    s.number_of_active_ants = number_of_active_ants
    alg=run_func(number_of_active_ants=s.number_of_active_ants, board_size=s.board_size, ant_locations=s.homes)
    #alg.grid.display()
    alg.set_map(the_map)
    #alg.grid.display()
    done = False
    s.steps = 0
    #shortest = astar(homes, the_map)
    #print "shortest path", shortest
    #if shortest is None:
    #    break
    i=0        
    while 1:
        done, num_of_pheromones = alg.single_step()
        if done:
            #s = '%s, %s, %s\n' % (shortest, i, num_of_pheromones)
    
            return i, num_of_pheromones
            #print "num of steps",i
            #print "num of pheromones", num_of_pheromones      
        i+=1 
  
MAPS_HOMES_PICKLE_FILENAME='maps_homes.pickle'
    
def make_random_map_homes_file():
    print "making list of random maps and homes into %s" % MAPS_HOMES_PICKLE_FILENAME
    pairs = list(generate_data())
    with open(MAPS_HOMES_PICKLE_FILENAME, 'w+') as f:
        cPickle.dump(pairs, f)
    
def make_params(the_map, homes):
    # IMPORTANT NOTE: don't change this, it is the key to the results database
    return cPickle.dumps((the_map, homes))

def main():
    if not os.path.exists(MAPS_HOMES_PICKLE_FILENAME):
        make_random_map_homes_file()
    with open(MAPS_HOMES_PICKLE_FILENAME, 'r') as f:
        map_home_pairs = cPickle.load(f)
    con = sqlite3.connect('ant_results.sqlite3')
    try:
        con.execute('create table results (params, result)')
    except sqlite3.OperationalError:
        pass
    for i, (the_map, homes) in enumerate(map_home_pairs):
        params = make_params(the_map, homes)
        if con.execute('select count(*) from results where params=?', [params]).fetchall()[0][0] > 0:
            continue
        print "calculating %d/%d" % (i, len(map_home_pairs))
        results = single_run(the_map, homes)
        con.execute('insert ?, ? into results', [params, cPickle.dumps(results)])
        con.commit()
    # create report

if __name__ == '__main__':
    main()
