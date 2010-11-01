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
grey = (50, 50, 50)
blue = (0, 0, 255)
red = (255, 0, 0)

DIRECTIONS = RIGHT, DOWN, LEFT, UP = 0, pi/2, pi, pi*3/2

class PyGameRenderer(Renderer):
    in_cell_poses = [(16, 16), (48, 48)]

    def __init__(self):
        import Final as F
        import pygame
        self.F = F
        self.screen = None
        params = [(F.EMPTY, None), (F.START, None),
            (F.UP_SYM,    UP),    (F.DOWN_SYM, DOWN),
            (F.RIGHT_SYM, RIGHT), (F.LEFT_SYM, LEFT)]
        self.ant_id_to_num = dict([(F.EMPTY, None), ('1', 1), ('2', 2)])
        self.arrow_cell2render = dict(params)
        pygame.init()

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
        self.obstacle = pygameutil.Sprite(filename='trap.png',
                                        target_width=cell_width,
                                        rotation=0)

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

    def _render_cell_contents(self, cell, x, y):
        F = self.F
        # perimeters
        arr = cell.get_for_arrow()
        w = 1
        cw = self.cell_width
        left, top, right, bottom = x*cw, y*cw, (x+1)*cw, (y+1)*cw
        in_left, in_top, in_right, in_bottom = (
            left+w, top+w, right-w, bottom-w)
        def draw(sprite, x, y):
            sprite.set_pos(x, y)
            self.screen.blit(sprite._sprite, sprite._rect)
        def frame(color, marg):
            self.screen.fill(color, (left, top, cw, marg))
            self.screen.fill(color, (left, top, marg, cw))
            self.screen.fill(color, (left, in_bottom, cw, marg))
            self.screen.fill(color, (in_right, top, marg, cw))
        def square(marg, color):
            self.screen.fill(color,
                (left + marg, top + marg, cw - 2 * marg, cw - 2 * marg))
        if cell.is_obstacle():
            #frame(color=grey, marg=cw*0.1)
            draw(self.obstacle, x * cw + cw / 2, y * cw + cw / 2)
            return
        ant_id = self.ant_id_to_num[cell.get_ant_ID()]
        if cell.get_back_arrow() == F.START:
            square(color={1:blue, 2:red}[ant_id], marg=w)
        dirs = [self.arrow_cell2render[a] for a in
                [cell.get_for_arrow(), cell.get_back_arrow()]]
        frame(color=black, marg=w)
        if ant_id == None and cell.get_ant_sym() in '*':
            print "BUG"
            import pdb; pdb.set_trace()
        if cell.get_ant_sym() in '*':
            square(color={1:blue, 2:red}[ant_id], marg=cw*0.3)
        for (x0, y0), dir in zip(self.in_cell_poses, dirs):
            if dir is None:
                continue
            if ant_id is None:
                import pdb; pdb.set_trace()
            draw(self.arrows[ant_id][dir], x*cw + x0, y*cw + y0)

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
        ant_locations = grid.get_ant_locations()
        for i in xrange(w):
            for j in xrange(h):
                cell = grid.grid[j][i]
                self._render_cell_contents(cell=cell, x=i, y=j)
                #print "%2s|%5s" % (has_ant,
                #      '%2s%2s' % tuple(' ' if x is None else ('%2.1f' % x) for x in dirs)),
            #print
        pygame.display.flip()

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
    goa.set_map(map)
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
