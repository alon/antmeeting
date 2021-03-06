#!/usr/bin/env python

from constants import *

def boardcopy(board):
    d = {}
    for k in board.keys():
        d[k] = board[k]
    return d

def getoptions(d, os, default):
    for o in os:
        if d.has_key(o):
            return d[o]
    return default

def withpos(grid):
    for l_i, l in enumerate(grid):
        for pos, c in enumerate(l):
            yield (pos, l_i), c
def handle_symb(s, c):
    if c == '1':
        handle_symb.starting_locations[0] = (s[0], s[1])
    elif c == '2':
        handle_symb.starting_locations[1] = (s[0], s[1])
    return {' ':NO_SYMBOL, '*':OBSTACLE}.get(c, NO_SYMBOL)

class FSMBlockObservable(object):
    """ Multiple ants version

    Notice: The ants have the same everything, except internal state and position:
     * same transfer function
     * running on the same board (just with differing positions)
    """
    def __init__(self, board_size, starting_locations, startstate, transfer, radius, grid=None):
        if grid is None:
            board_x, board_y = board_size
            self._positions = [(i%board_x, int(i/board_x)) for i in range(board_x * board_y)]
            self._board = dict([(s, NO_SYMBOL) for s in self._positions])
        else:
            board_size = len(grid), len(grid[0])
            handle_symb.starting_locations = starting_locations
            self._board = dict([(s, handle_symb(s, c)) for s, c in withpos(reversed(grid))])
        self._board_size = board_size
        self._radius = max(0, int(radius))
        self._transfer = transfer
        self._pos = list(starting_locations) # make a copy
        self._num_ants = len(self._pos)
        self._currentstate = [startstate for i in xrange(self._num_ants)]
        self._stopped = [False] * self._num_ants
        # cache
        self._laststep = 0
        self._cache = {0: boardcopy(self._board)}
    
    def asciidump(self):
        ascii = [
            [self._board[(j, i)] for j in xrange(self._board_size[0])]
                for i in reversed(range(self._board_size[1]))]
        for i, p in enumerate(self._pos):
            ascii[self._board_size[1] - p[1] - 1][p[0]] = str(i+1)
        return '\n'.join(''.join(l) for l in ascii)

    def step(self):
        for i_ant in xrange(self._num_ants):
            self._step(i_ant)
        self._laststep += 1
        self._cache[self._laststep] = boardcopy(self._board)

    def board_with_ant(self, i_me, x, y):
        xy = (x,y)
        if xy not in self._board.keys():
            return OUT_OF_BOARD
        if xy in self._pos:
            if self._pos.index(xy) != i_me:
                return ANT_SYMBOL
        if self._board[(x,y)] == OBSTACLE:
            return X
        return self._board[(x,y)]

    def _step(self, i_ant):
        if self._stopped[i_ant]: return
        if self._radius == 0:
            symbols = self._board[self._currentstate[i_ant]]
        else:
            r = self._radius
            cur_x, cur_y = self._pos[i_ant]
            xs = list(range(cur_x - r, cur_x + r + 1))
            ys = list(range(cur_y - r, cur_y + r + 1))
            symbols = tuple([tuple([self.board_with_ant(i_ant, x, y)
                                    for x in xs]) for y in ys])
        print "symbols =", symbols
        # first look for a no symbols clause, then look for with symbols
        nextstate, action, written = getoptions(self._transfer, [
            self._currentstate[i_ant], (self._currentstate[i_ant], symbols)],
                (self._currentstate[i_ant], None, None))
        if written is not None:
            self._board[self._pos[i_ant]] = written
        board_x, board_y = self._board_size
        if action == A_MEET:
            print "they meet at last"
        if action in [A_STOP, A_MEET]:
            self._stopped[i_ant] = True
            return
        self._pos[i_ant] = {
            A_LEFT: lambda (x, y): (max(0, x-1), y),
            A_RIGHT: lambda (x, y): (min(x+1, board_x-1), y),
            A_UP: lambda (x, y): (x, min(board_y-1, y+1)),
            A_DOWN: lambda (x, y): (x, max(y-1, 0)),
        }.get(action, lambda (x, y): (x,y))(self._pos[i_ant])
        self._currentstate[i_ant] = nextstate

    def getState(self, step):
        step = max(0, int(step))
        for x in range(step - self._laststep):
            self.step()
        return self._cache[step]

    def getStateRelative(self, rel):
        return self.getState(self._laststep - rel)

    def dump(self):
        xy = self._pos
        xs = range(0, self._board_size[0])
        ys = range(0, self._board_size[1])
        board_at_xy = [self._board[xy_i] for xy_i in xy]
        for xy_i in xy: self._board[xy_i] = '*'
        print "step:", self._laststep
        print "\n".join(reversed([''.join([str(self._board[(x,y)]) for x in xs]) for y in ys]))
        for xy_i,old_contents in zip(xy, board_at_xy): self._board[xy_i] = old_contents

def compute_circle_transfer(n):
    """
    return a FSM where the ant does a circle around the perimieter
    . This fsm is finite for finite n, but not O(1).

    return: nextstate, action, written
    """
    d = {}
    for x in range(n-1):
        d[(x, 0)] = ((x+1, 0), A_RIGHT, None)
    for y in range(n-1):
        d[(n-1, y)] = ((n-1, y+1), A_DOWN, None)
    for x in range(n-1):
        d[(x+1, n-1)] = ((x, n-1), A_LEFT, None)
    for y in range(n-1):
        d[(0, y+1)] = ((0, y), A_UP, None)
    return (0, 0), d # start state, transfer dictionary

###################################################################

def map2sym1(m):
    """
    You provide the map as
"'""
xyz
abc
qwe
"'""
    Where the top line is the one in the up direction, the bottom is the down direction
    (down = lower y then up)
    Where space is the NO_SYMBOL symbol
    and it returns it as a symbols list that FSM can match up.
    """
    lines = [x for x in m.split('\n') if len(x) > 0]
    return tuple(reversed([tuple(l) for l in lines]))

from spiral import base_spiral
from meet import base_meet
spiral_transfer = dict([
    ((None, map2sym1(ls)), (None, act, w)) for \
    ls, act, w in base_spiral])
meet_transfer = dict([
    ((None, map2sym1(ls)), (None, act, w)) for \
    ls, act, w in base_meet])


def make_meet_fsm(board_size, starting_locations, grid):
    return FSMBlockObservable(
            board_size = board_size,
            starting_locations = starting_locations,
            transfer=meet_transfer,
            startstate = None, # unused
            radius=1,
            grid=grid)


###################################################################

def testFSM(fsm, steps=20):
    for i in range(steps):
        fsm.dump()
        fsm.step()
        if fsm.getStateRelative(0) == fsm.getStateRelative(1):
            print "no change in last state"
            return
    fsm.dump()

board_size = (70, 70)
starting_locations = (
    (20, 20),
    (26, 19)
)

def make_fsm(transfer, startstate, radius,
             starting_locations = starting_locations,
             board_size = board_size):
    return FSMBlockObservable(
        board_size = board_size,
        starting_locations = starting_locations,
        transfer = transfer, startstate = startstate, radius=radius)

def test():
    n = 15
    steps = 95
    circle_start, circle_transfer = compute_circle_transfer(n)
    roundfsm = make_fsm(
            transfer = circle_transfer,
            startstate = circle_start,
            radius=1)
    meetfsm = make_fsm(
            transfer=meet_transfer,
            startstate = None, # unused
            radius=1)
    spiralfsm = make_fsm(
            transfer=spiral_transfer,
            startstate = None, # unused
            radius=1)
    for fsm, steps in [
            #(roundfsm, n*4),
            (meetfsm, steps),
            #(spiralfsm, STEPS),
        ]:
        testFSM(fsm, steps)

if __name__ == '__main__':
    test()

