"""
keep all the rendering functions in one place

currently:
render to ascii
render to pdf (requires pyx)
"""


__all__ = ['Renderer', 'AsciiRenderer', 'render_factories']

from math import pi

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
        self.arrows = dict([
            (rotation, pygameutil.Sprite(filename='right_arrow.png',
                target_width=cell_width,
                rotation=rotation))
            for rotation in DIRECTIONS
            ])

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

    def _render_cell_contents(self, i, j, has_ant, dirs):
        # perimeters
        w = 1
        cw = self.cell_width
        left, top, right, bottom = i*cw, j*cw, (i+1)*cw, (j+1)*cw
        in_left, in_top, in_right, in_bottom = (
            left+w, top+w, right-w, bottom-w)
        self.screen.fill(black, (left, top, cw, w))
        self.screen.fill(black, (left, top, w, cw))
        self.screen.fill(black, (left, in_bottom, cw, w))
        self.screen.fill(black, (in_right, top, w, cw))
        if has_ant:
            self.screen.fill({1:blue, 2:red}[has_ant],
                (left+w, top+w, cw-2*w, cw-2*w))
        for (x0, y0), dir in zip(self.in_cell_poses, dirs):
            print x0, y0
            if dir is None:
                continue
            arr = self.arrows[dir]
            arr.set_pos(i*cw + x0, (j + 1)*cw + 32 - y0)
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
            (F.UP_SYM,UP), (F.DOWN_SYM,DOWN),
            (F.RIGHT_SYM,RIGHT), (F.LEFT_SYM,LEFT)]
        arrow_cell2render = dict(params)
        ant_locations = grid.get_ant_locations()
        for i in xrange(w):
            for j in xrange(h):
                cell = grid.grid[i][j]
                self._render_cell_contents(i=i, j=j,
                    has_ant=(0 if (i, j) not in ant_locations else
                        ant_locations.index((i,j)) + 1), dirs=[
                        arrow_cell2render[a] for a in 
                            [cell.get_for_arrow(), cell.get_back_arrow()]])
        pygame.display.flip()

def test_run():
    import run
    import grid_generators
    map=grid_generators.grid_makers[0](size=(10,10),p_empty=0.9)
    goa=run.GOARun('',board_size=(10,10),ant_locations=[(1,1), (3,3)])
    run.randants(goa)
    renderer = PyGameRenderer()
    for i in xrange(1):
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
