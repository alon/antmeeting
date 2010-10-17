"""
keep all the rendering functions in one place

currently:
render to ascii
render to pdf (requires pyx)
"""


__all__ = ['Renderer', 'AsciiRenderer', 'render_factories']

from math import pi
import random

class Renderer(object):
  
    def render(self, grid, title=None):
        raise NotImplemented("render")

class AsciiRenderer(Renderer):
    
    def render(self, grid, step_num, title=None):
        print title
        for i in range(0, grid.size[0]+1):
            for j in range(0, grid.size[1]+1):
                print grid[i,j],
            print " "
        print " "

# RGB
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)

DIRECTIONS = RIGHT, DOWN, LEFT, UP = 0, pi/2, pi, pi*3/2

class PyGameRenderer(Renderer):
    in_cell_poses = [(16, 16), (48, 48)]

    def __init__(self):
        import pygame
        pygame.init()
        self.screen = None

    def create_window(self, (grid_width, grid_height)):
        import pygame
        import pygameutil

        if self.screen:
            return
        cell_width = 64 # TODO - take from red size
        self.size = (cell_width*grid_width, cell_width*grid_height)
        self.grid_size = (grid_width, grid_height)
        if max(self.size) > 800:
            print "%d is too large, size is %s" % (n, self.size)
            raise SystemExit
        self.screen = pygame.display.set_mode(self.size,
            pygame.DOUBLEBUF) # pygame.HWSURFACE
        self.cell_width = cell_width
        target_width = cell_width / 2
        self.arrows = dict([(ant_num, dict([
            (rotation, pygameutil.Sprite(filename='right_arrow_%s.png' % ('red' if ant_num == 2 else 'blue'),
                target_width=cell_width,
                rotation=-rotation))
            for rotation in DIRECTIONS
            ])) for ant_num in xrange(1, 3)])

    def _render_grid(self):
        """
         | |
        -----
         | |
        -----
         | |
        """
        w = 3
        cw = self.cell_width
        win_w, win_h = self.size
        for i in xrange(self.grid_size[0]+1):
            self.screen.fill(white, (i*cw, 0, i*cw+w, win_h))
        for i in xrange(self.grid_size[1]+1):
            self.screen.fill(white, (0, i*cw, win_w, i*cw+w))

    def _render_cell_contents(self, ant_id, x, y, has_ant, dirs, home):
        import Final as F
        # perimeters
        w = 1
        cw = self.cell_width
        left, top, right, bottom = x*cw, y*cw, (x+1)*cw, (y+1)*cw
        in_left, in_top, in_right, in_bottom = (
            left+w, top+w, right-w, bottom-w)
        self.screen.fill(black, (left, top, cw, w))
        self.screen.fill(black, (left, top, w, cw))
        self.screen.fill(black, (left, in_bottom, cw, w))
        self.screen.fill(black, (in_right, top, w, cw))
        def square(marg, color):
            self.screen.fill(color,
                (left + marg, top + marg, cw - 2 * marg, cw - 2 * marg))
        if home:
            square(color={1:blue, 2:red}[home], marg=w)
        if has_ant:
            square(color={1:blue, 2:red}[has_ant], marg=cw*0.3)
        for (x0, y0), dir in zip(self.in_cell_poses, dirs):
            if dir is None:
                continue
            arr = self.arrows[ant_id][dir]
            arr.set_pos(x*cw + x0, y*cw + y0)
            self.screen.blit(arr._sprite, arr._rect)

    def render_arrows(self):
        for i, (dir, arr) in enumerate(self.arrows.items()):
            for j in xrange(4):
                arr.set_pos(200+i*40,200+j*40)
                self.screen.blit(arr._sprite, arr._rect)
        pygame.display.flip()

    def render(self, grid, step_num, title=None):
        import pygame
        import Final as F

        self.create_window(grid.size)
        self.screen.fill(white,(0, 0, self.size[0], self.size[1]))
        if title is not None:
            pygame.display.set_caption(title)
        w, h = grid.size
        params = [(F.EMPTY, None), (F.START, None),
            (F.UP_SYM,    UP),    (F.DOWN_SYM, DOWN),
            (F.RIGHT_SYM, RIGHT), (F.LEFT_SYM, LEFT)]
        ant_id_to_num = dict([(F.EMPTY, None), ('1', 1), ('2', 2)])
        arrow_cell2render = dict(params)
        ant_locations = grid.get_ant_locations()
        for i in xrange(w):
            for j in xrange(h):
                cell = grid.grid[j][i]
                home = None if cell.get_back_arrow() != F.START else int(cell.get_ant_ID())
                has_ant = (0 if (j, i) not in ant_locations else
                        ant_locations.index((j, i)) + 1)
                dirs = [arrow_cell2render[a] for a in 
                        [cell.get_for_arrow(), cell.get_back_arrow()]]
                arr = cell.get_for_arrow()
                ant_id = ant_id_to_num[cell.get_ant_ID()]
                self._render_cell_contents(ant_id=ant_id, x=i, y=j,
                    has_ant=has_ant, dirs=dirs, home=home)
                #print "%2s|%5s" % (has_ant,
                #      '%2s%2s' % tuple(' ' if x is None else ('%2.1f' % x) for x in dirs)),
            #print
        pygame.display.flip()

def main(homes = [(2,2), (3,7)]):
    import run
    import pygame
    from pygame import KEYDOWN
    import grid_generators
    map = grid_generators.grid_makers[0](size=(10,10), p_empty=0.9)
    board_size = (10, 10)
    steps = 1
    cont = True
    renderer = PyGameRenderer()
    num = 0
    action = lambda x, y: x + y
    while cont:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == KEYDOWN and event.unicode == 'q':
                cont = False
            elif event.type == KEYDOWN:
                if event.unicode == 'a':
                    steps += 1
                elif event.unicode == 'z':
                    steps = max(0, steps - 1)
                elif ord('0') <= event.key <= ord('9'):
                    num = num*10 + event.key - ord('0')
                elif event.unicode == '-':
                    action = lambda x, y: x - y
                elif event.key == 13:
                    steps = max(0, action(steps, num))
                    num = 0
                    action = lambda x, y: x + y
            pygame.display.set_caption(str(steps))
        if cont:
            goa=run.GOARun('', board_size=board_size, ant_locations=homes)
            done = False
            for i in xrange(steps):
                done = goa.single_step()
                if done:
                    done_step = i
                    break
            if done:
                pygame.display.set_caption('MEETING - %d (%d)' % (done_step, steps))
            renderer.render(goa.grid, 1)
            pygame.time.delay(10)

def render_grid(board_size=(10,10)):
    import Final
    grid = Final.GOAGrid(board_size = board_size)
    renderer = PyGameRenderer()
    renderer.render(grid, 1)
    return grid, renderer

def test_run():
    import run
    import grid_generators
    map = grid_generators.grid_makers[0](size=(10,10), p_empty=0.9)
    board_size = (10, 10)
    #homes = [[random.randint(2, x-3) for x in board_size] for i in xrange(2)]
    homes = [(2,2), (3,7)]
    goa=run.GOARun('', board_size=board_size, ant_locations=homes)
    renderer = PyGameRenderer()
    for i in xrange(13):
        goa.single_step()
    renderer.render(goa.grid, 1)
    return renderer, goa, map

render_factories = [AsciiRenderer]

try:
    import pyx
except:
    print "no Pyx - no pyx rendering"
else:
    from render_to_pdf import PyxRenderer
    render_factories.insert(0, PyxRenderer) # make sure this is the first renderer created

import string
lower = set(string.lowercase)
        
def create_renderers(**kw):
    ret = []
    def to_lower(n):
        """AlonHanan -> alon_hanan"""
        return n[:1].lower() + ''.join([(c if c in lower else '_'+c.lower()) for c in n[1:]])
    for f in render_factories:
        lower_name = to_lower(f.__name__)
        if lower_name not in kw: continue
        ret.append(f(**kw[lower_name]))
    return ret
