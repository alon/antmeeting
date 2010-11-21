import AStar
import run
from test

def astar(homes, zmap):
    startpoint, endpoint = homes = map(tuple, homes)
    width, height = len(zmap), len(zmap[0])
    trans = {'*':-1, ' ':1}
    snart = {-1:'*', 1:' '}
    mapdata = dict([((x,y),trans[zmap[x][y]]) for x,y in xys(width, height)])
    def pos(mapdata, x, y):
        if (x,y) in homes:
            return str(homes.index((x,y)) + 1)
        return snart[mapdata[(x,y)]]
    for x in range(width):
        print ''.join(pos(mapdata,x,y) for y in range(height))
    astar = AStar.AStar(AStar.SQ_MapHandler(mapdata, width, height))
    start = AStar.SQ_Location(startpoint[0],startpoint[1])
    end = AStar.SQ_Location(endpoint[0],endpoint[1])
    p = astar.findPath(start,end)
    if p:
        return len(p.nodes)
    else:
        return None

def randomize():
    zmap, homes = make_map_with_ants_on_vacancies(
        default_homes=default_homes,
        make_map=make_map, make_homes=make_homes)
    return zmap, homes

def generate_data():
    for i in xrange(10):
        return randomize()

for map, homes in generate_data():
    goa=run.GOARun('', board_size=s.board_size, ant_locations=s.homes)
    #goa.grid.display()
    goa.set_map(s.zmap)
    #goa.grid.display()
    done = False
    for i in xrange(s.steps):
        done = goa.single_step()
        if done:
            break


