#!/usr/bin/env pypy

from collections import namedtuple
from multiprocessing import Pool, cpu_count, Process, active_children
from glob import glob
import itertools
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

def astar(homes, zmap, verbose=False):
    startpoint, endpoint = homes = map(tuple, homes)
    width, height = len(zmap), len(zmap[0])
    trans = {'*':-1, ' ':1}
    mapdata = dict([((x,y),trans[zmap[x][y]]) for x,y in xys(width, height)])
    if verbose:
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

def generate_map_homes_data(N, number_of_runs=50):
    """ generate pairs of (map, homes)
    5 movingai maps, {original (closed), open}
    5 fixed mazes, {closed,open}
    5 {10,20,30}% map {closed,open}
    """
    print "using N=%s" % N
    def iter_maps():
        for i in xrange(5):
            yield maps.read_maze('maze_%03d.map' % i)
    for m in iter_maps():
        rows = len(m)
        max_col = max(len(x) for x in m)
        if rows > N or max_col > N:
            print "Warning: you are chunking your maze from (%d,%d) to %d" % (
                    rows, max_col, N)
    fixed_mazes = [
        lambda maze=maps.chunk(N, maps.read_maze('maze_%03d.map' % i)):
            maze for i in xrange(5)]
    fixed_percent = sum([
            [lambda: maps.grid_generators.grid_makers[0](size=(N,N), p_empty=p_empty)
                for p_empty in [p]*5]
                 for p in [0.9, 0.8, 0.7]
        ],
        [])
    # movingai maps - not chunked. This is important.
    movingai_closed = [lambda maze=maps.read_movingai(m): maze for m in glob('movingai/closed/*.map')]
    movingai_open = [lambda maze=maps.read_movingai(m): maze for m in glob('movingai/open/*.map')]
    p = itertools.product
    c = itertools.chain
    def do_one((maze_gen, extend_map)):
        map_count = 0
        while map_count < number_of_runs:
            thrown = 0
            zmap, homes = maps.make_map_with_ants_on_vacancies(
                 default_homes=[(2,2), (3,7)], make_map=maze_gen, make_homes=maps.random_homes)
            a = astar(homes, zmap)
            if a is None or a < 20:
                thrown += 1
                continue
            print("ASTAR: %d (thrown %d)" % (a, thrown))
            if extend_map:
                xmap = extend_and_add_trap_to_map(zmap)
            else:
                xmap = zmap
            return xmap, homes, {'closed': not extend_map}
            map_count += 1
            #astar, ROA, ROA one ant, GOA, GOA one ant
            #    time, num of pheromones

    pairs = c(p(movingai_closed, [False]), p(movingai_open, [True]),
              p(fixed_mazes + fixed_percent, [False, True]))
    # XXX - can always turn this back to a yield, but then need to move the
    # consumer into the p.map, into do_one, to gain multiprocessing?
    ret = pmap_interleaved(pool, do_one, pairs)
    return ret

def interleave(it, ncpu):
    l = list(it)
    indices = [xrange(x, len(l), ncpu) for x in range(ncpu)]
    reordered = sum([[l[i] for i in single] for single in indices], [])
    assert(len(reordered) == len(l))
    return reordered

def undo_interleave(l, ncpu):
    """ not symmetric with slice - wants a list """
    ret = [None for i in len(rei)]
    indices = [xrange(x, len(l), ncpu) for x in range(ncpu)]
    i_out = 0
    for single in indices:
        for i in single:
            ret[i] = l[i_out]
            i_out += 1
    return ret

def pmap_interleaved(pool, do_one, it):
    """
    pool.map l with do_one, but instead of splitting linearly split
    by offsets:
    instead of [A, A, B, B, C, C, D, D]
    do         [A, B, C, D, A, B, C, D]
    Returns the results in the original order
    """
    l = list(it)
    indices = [xrange(x, len(l), 4) for x in range(4)]
    reordered = sum([[l[i] for i in single] for single in indices], [])
    assert(len(reordered) == len(l))
    rei = results_interleaved = pool.map(do_one, l)
    ret = [None for i in len(rei)]
    i_out = 0
    for single in indices:
        for i in single:
            ret[i] = rei[i_out]
            i_out += 1
    return ret

class Data(object):
    pass

def single_run(the_map, homes):
    a = [astar(homes, the_map)]
    a.extend([single_run_alg(run_func, the_map, homes) for run_func in [run.GOARun, run.COARun]])
    a.extend([single_run_alg_one_ant(run_func, the_map, homes) for run_func in [run.GOARun, run.COARun]])
    return a

def single_run_alg_one_ant(run_func, the_map, homes):
    return single_run_alg(run_func, the_map, homes, number_of_active_ants=1)

Results=namedtuple('Results', 'alg, steps, pheromones')

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
            return Results(alg=run_func.__name__, steps=i, pheromones=num_of_pheromones)
            #print "num of steps",i
            #print "num of pheromones", num_of_pheromones
        i+=1
    return None,None

def map_filename(N):
    return os.path.join(str(N), MAPS_HOMES_PICKLE_FILENAME)

def make_map_homes_file(random_map_N):
    filename = map_filename(random_map_N)
    if os.path.exists(filename):
        return filename
    os.makedirs(str(random_map_N))
    print "making list of random maps and homes into %s" % filename
    data = list(generate_map_homes_data(random_map_N))
    with open(filename, 'w+') as f:
        cPickle.dump(data, f)
    return filename

def make_params(the_map, homes):
    # IMPORTANT NOTE: don't change this, it is the key to the results database
    return cPickle.dumps((the_map, homes))

def results_filename(N):
    return os.path.join(str(N), 'ant_results.sqlite3')

def ctrl_c_handler(*args):
    print "Ctrl-C caught (%d), exiting" % os.getpid()
    for c in active_children():
        print "terminating %s" % c
        c.terminate()
    sys.exit(1)

def do_multiple(N):
    if not N:
        print "TODO: pick up N from the size of the non random maps"
        raise SystemExit
    filename = make_map_homes_file(random_map_N=N)
    print "loading map file %s" % filename
    with open(filename, 'r') as f:
        map_home_data = cPickle.load(f)
    print "total %d datum required" % len(map_home_data)
    dbfile = results_filename(N)
    print "opening databsase %s" % dbfile
    con = sqlite3.connect(dbfile)
    try:
        print "creating new results table"
        con.execute('create table results (params, result)')
    except sqlite3.OperationalError:
        pass
    inputs = []
    for i, (the_map, homes, closed) in enumerate(map_home_data):
        params = make_params(the_map, homes)
        if con.execute('select count(*) from results where params=?', [params]).fetchall()[0][0] > 0:
            continue
        inputs.append((i, the_map, homes))
    results_missing = len(inputs)
    def do_single((i, the_map, homes)):
        params = make_params(the_map, homes)
        print "calculating %d/%d" % (i, results_missing)
        results = single_run(the_map, homes)
        return i, params, results
    print "missing %d datum" % results_missing
    print "running parallel on %d cpus" % cpu_count()
    p = Pool(cpu_count())
    sliced_inputs = interleave(inputs, cpu_count())
    calculated = 0
    for i, params, results in pool.imap_unordered(do_single, sliced_inputs):
        calculated += 1
        print "got results for %s (%d/%d)" % (i, calculated, results_missing)
        con.execute('insert into results values (?, ?)', [params, cPickle.dumps(results)])
        con.commit()

def do_single(map_filename, homes):
    the_map = maps.read_movingai(map_filename)
    params = make_params(the_map, homes)
    results = single_run(the_map, homes)
    print results[1]._fields
    print results[0], [tuple(r) for r in results[1:]]
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-N', type=int, default = 256)
    parser.add_argument('--map')
    parser.add_argument('--a1')
    parser.add_argument('--a2')
    args = parser.parse_args(sys.argv[1:])
    if args.map:
        if not args.a1 or not args.a2:
            parser.print_usage()
            sys.exit(1)
        do_single(map_filename=args.map, homes=[map(int, x.split(',')) for x in [args.a1, args.a2]])
    else:
        do_multiple(args.N)
    # create report

if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c_handler)
    pool = Pool(cpu_count())
    main()
    #map_tester()
