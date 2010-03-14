from random import random as randunity
from random import sample

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

grid_makers = [make_rand_cell, make_constant_ratio]

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
    