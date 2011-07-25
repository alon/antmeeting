#!/usr/bin/env python

import AStar
import run
import maps
import sqlite3
import os
import cPickle
import argparse
import sys
import signal

MAPS_HOMES_PICKLE_FILENAME='maps_homes.pickle'
#N=100 # limit screen size
#MAX_STEPS=N*N*N    
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

def extend_and_add_trap_to_map(m):
    new_map = m + ([[' ' for i in range(len(m[0]))] for j in range(len(m))])
    i = 0
    for i in range(len(m[0])):
        new_map[len(m) + 1][i] = ('*' if i != len(m[0])/2 else ' ')
    return new_map
    
def map_tester():
    the_map = extend_and_add_trap_to_map([[' ' for i in range(10)] for j in range(10)])
    print '\n'.join('%d: %r' % (i, ''.join(l)) for i,l in enumerate(the_map))

def generate_data(N):
    """ generate pairs of (map, homes) """
    print "using N=%s" % N
    # 5 fixed mazes
    fixed_mazes = [lambda maze=maps.chunk(N, maps.read_maze('maze_%03d.map' % i)): maze for i in xrange(5)]
    # 5 10% map, 5 20% map, 5 30% map
    fixed_percent = sum(
        [
            [lambda: maps.grid_generators.grid_makers[0](size=(N,N), p_empty=p_empty)
                for p_empty in [p]*5]
         for p in [0.9, 0.8, 0.7]
        ],
        [])
    for maze_gen in fixed_mazes + fixed_percent:
        map_count = 0
        while map_count < 10:
            zmap, homes = maps.make_map_with_ants_on_vacancies(
                 default_homes=[(2,2), (3,7)], make_map=maze_gen, make_homes=maps.random_homes)
            a = astar(homes, zmap)
            if a is None:
                continue  
            print "ASTAR: ", a
            xmap = extend_and_add_trap_to_map(zmap)
            yield xmap, homes
            map_count += 1
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
    return single_run_alg(run_func, the_map, homes, number_of_active_ants=1)

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
    while True:
        done, num_of_pheromones = alg.single_step()
        if done:
            #s = '%s, %s, %s\n' % (shortest, i, num_of_pheromones)
            return i, num_of_pheromones
            #print "num of steps",i
            #print "num of pheromones", num_of_pheromones
        i+=1
    return None,None

def map_filename(N):
    return os.path.join(str(N), MAPS_HOMES_PICKLE_FILENAME)

def make_random_map_homes_file(N):
    filename = map_filename(N)
    if os.path.exists(filename):
        return filename
    os.makedirs(str(N))
    print "making list of random maps and homes into %s" % filename
    pairs = list(generate_data(N))
    with open(filename, 'w+') as f:
        cPickle.dump(pairs, f)
    return filename

def make_params(the_map, homes):
    # IMPORTANT NOTE: don't change this, it is the key to the results database
    return cPickle.dumps((the_map, homes))

def results_filename(N):
    return os.path.join(str(N), 'ant_results.sqlite3')

def ctrl_c_handler(*args):
    print "Ctrl-C caught, exiting"
    sys.exit(1)

signal.signal(signal.SIGINT, ctrl_c_handler)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-N', type=int)
    args = parser.parse_args(sys.argv[1:])
    N = args.N
    filename = make_random_map_homes_file(N)
    print "loading map file %s" % filename
    with open(filename, 'r') as f:
        map_home_pairs = cPickle.load(f)
    print "have to calculate %d pairs" % len(map_home_pairs)
    dbfile = results_filename(N)
    print "opening databsase %s" % dbfile
    con = sqlite3.connect(dbfile)
    try:
        print "creating new results table"
        con.execute('create table results (params, result)')
    except sqlite3.OperationalError:
        pass
    for i, (the_map, homes) in enumerate(map_home_pairs):
        params = make_params(the_map, homes)
        if con.execute('select count(*) from results where params=?', [params]).fetchall()[0][0] > 0:
            print "%d/%d already calculated" % (i, len(map_home_pairs))
            continue
        print "calculating %d/%d" % (i, len(map_home_pairs))
        results = single_run(the_map, homes)
        con.execute('insert into results values (?, ?)', [params, cPickle.dumps(results)])
        con.commit()
    # create report

if __name__ == '__main__':
    main()
    #map_tester()
