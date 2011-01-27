from random import random as randunity
from random import sample
import random

def grid_from_iter(size, it):
    g = [[' ' for x in xrange(size[1])] for y in xrange(size[0])]
    for x, y in it:
        g[x][y] = '*'
    return g

def grider(it_f):
    def f(size, **kw):
        return grid_from_iter(size=size, it=it_f(size=size, **kw))
    f.iter = it_f
    f.func_name = it_f.func_name
    return f

@grider
def make_rand_cell(size, p_empty):
    for x in xrange(size[0]):
        for y in xrange(size[1]):
            if randunity() >= p_empty:
                yield x, y

@grider
def make_constant_ratio(size, p_empty):
    num_occupied = int(size[0]*size[1]*(1-p_empty))
    possible = set(sum(([(x, y) for x in xrange(size[1])] for y in xrange(size[0])), []))
    for x, y in sample(possible, num_occupied):
        yield x, y

def maze_by_iterative_partition(size,p_empty):
    g = [[' ' for x in xrange(size[1])] for y in xrange(size[0])]
    complexity = int(0.75*(5*(size[0]+size[1])))
    density    = int((1-p_empty)*(size[0]//2*size[1]//2))  
    for x in xrange(size[1]):
        g[x][0] = g[x][size[1]-1] = "*"
    for y in xrange(size[0]):
        g[0][y] = g[size[0]-1][y] = "*"
    for i in range(density):
        x, y = random.randint(0,size[1])-1, random.randint(0,size[0])-1
        print x, y
        g[x][y] = "*"
        for j in range(complexity):
            neighbours = []
            if x > 1:           neighbours.append( (x-2,y) )
            if x < size[1]-2:   neighbours.append( (x+2,y) )
            if y > 1:           neighbours.append( (x,y-2) )
            if y < size[0]-2:   neighbours.append( (x,y+2) )
            if len(neighbours):
                x_,y_ = neighbours[random.randint(0,len(neighbours)-1)]
                if g[x_][y_] == " ":
                    g[x_][y_] == "*"
                    g[x_+(x-x_)//2][y_+(y-y_)//2] = "*"
                    x, y = x_, y_
    # partition by iteration
    return g
        
grid_makers = [make_rand_cell, make_constant_ratio, maze_by_iterative_partition]

##################################################################

def printmap(g):
    print '\n'.join(''.join(l) for l in g)

def num_occupied(g):
    return sum(sum(1 if c == '*' else 0 for c in l) for l in g)

def test():
    size = (10,10)
    for f, params in [(make_rand_cell,      dict(p_empty=0.8)),
                      (make_constant_ratio, dict(p_empty=0.8))]: # you get 19! not an error!
        # use f.iter for adding obstacles to more coplex grid (i.e. GOAGrid)
        print f.iter
        g = f(size=size, **params)
        print num_occupied(g)
        printmap(g)


if __name__ == '__main__':
    test()
    
