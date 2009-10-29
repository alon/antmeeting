import os
from string import ascii_lowercase
from pyx import *

grey = color.rgb(0.5,0.5,0.5)

def center_of_gravity(grid, ant_num):
    x, y = 0, 0
    count = 0
    ant_str = str(ant_num)
    for _y, l in enumerate(grid.grid):
        for _x, c in enumerate(l):
            if c.get_ant_ID() == ant_str:
                x += _x
                y += _y
                count += 1
    print "cog: used %s" % count
    return (float(x) / count, float(y) / count)

def create_pdf(filename, canvases, num_in_row = 5, with_numbering = True):
    c = canvas.canvas()
    # all subcanvases should be the same size
    bbox = canvases[0].bbox()
    w, h = bbox.width(), bbox.height()
    w += 0.5
    h += 0.75
    if with_numbering:
        h += 1.0
    for i, can in enumerate(canvases):
        x_mid = w * (i % num_in_row)
        y_mid = -h * (i / num_in_row)
        c.insert(can, [trafo.translate(x_mid, y_mid)])
        if with_numbering:
            c.text(w/2 + x_mid - 2, y_mid - 2 , '(%s)' % ascii_lowercase[i], [text.size(5)])
    #c.writePDFfile(self.filename)
    c.writeEPSfile(filename)
    run('epstopdf %s > %s' % ('%s.eps' % filename, '%s.pdf' % filename))
    run('pdf2svg %s %s' % ('%s.pdf' % filename, '%s.svg' % filename))
    # to png
    run('convert %s %s' % ('%s.svg' % filename, '%s.png' % filename))

def run(cmd):
    print "running %s" % cmd
    os.system(cmd)

class PyxRenderer(object):

    def __init__(self, filename = None, num_in_row=5, draw_slide_title=False):
        self.i = 0
        self.filename = filename or 'grid.pdf'
        self.canvases = []
        self._draw_slide_title = draw_slide_title
        self.num_in_row = num_in_row

    def create_pdf(self):
        c = canvas.canvas()
        # all subcanvases should be the same size
        bbox = self.canvases[0].bbox()
        w, h = bbox.width(), bbox.height()
        w += 0.5
        h += 0.5
        for i, can in enumerate(self.canvases):
            c.insert(can, [trafo.translate(
                w * (i%self.num_in_row),
                -h * (i/self.num_in_row))])
        #c.writePDFfile(self.filename)
        c.writeEPSfile(self.filename)

    def draw_walls(self, c, grid):
        BOARD_SIZE = grid.render_size
        # verticals
        for i in range(0, BOARD_SIZE[1] + 2):
            c.stroke(path.line(i - 0.5, -0.5, i - 0.5, BOARD_SIZE[0] + 0.5), [grey])
        # horizontals
        for i in range(0, BOARD_SIZE[0] + 2):
            c.stroke(path.line( -0.5, i - 0.5, BOARD_SIZE[1] + 0.5, i - 0.5), [grey])
        # wrapping rectangle
        c.stroke(path.rect(-0.5, -0.5, BOARD_SIZE[0] + 1.0, BOARD_SIZE[1] + 1.0), [style.linewidth(0.1)])

    def draw_numbers(self, c, grid):
        from string import ascii_uppercase
        for x in xrange(grid.render_size[0]+1):
            c.text( -0.05 + x, -1.0, str(x+1))
        for y in xrange(grid.render_size[1]+1):
            c.text(-1.0, -0.1 + y, str(y+1))

    def render(self, grid, title):
        self.max_x, self.max_y = BS = grid.render_size
        self.i += 1
        c = canvas.canvas()
        grey = color.rgb(0.5,0.5,0.5)
        numbers_color = color.rgb(0.3, 0.3, 0.3)
        self.draw_walls(c, grid)
        self.draw_numbers(c, grid)
        ant_ids = range(len([x for x in grid.ants if x is not None]))
        # grey numbers behind the stuff
        for i in ant_ids:
            txt = str(i+1)
            try:
                ant_home = grid.get_ant_home(i)
                ant_location = grid.get_ant_location(i)
            except:
                import pdb; pdb.set_trace()
            #cx, cy = center_of_gravity(grid, ant_num)
            #print "cog =", cx, cy
            for x, y in ant_home, ant_location:
                # TODO - larger text
                c.text(y + 0.3, BS[0] - x + 0.2, txt, [text.halign.boxcenter, text.halign.flushcenter, numbers_color, text.size(5), ]) #style.linewidth.THick

        # draw cell contents (delegated)
        queue = []
        for i in range(0, BS[0]+1): # +1
            for j in range(0, BS[1]+1): # +1
                #self.render_cell(grid[i,j], c, i, j)
                # grid.render_cell returns a list of what's and functions
                for what, cmd in grid.render_cell(grid[i,j], c=c, i=i, j=j):
                    if what == 'ant':
                        cmd()
                    else:
                        queue.append(cmd)
        for cmd in queue: cmd()

        #c.writeEPSfile("grid_%04d.eps" % self.i)
        if self._draw_slide_title:
            # draw title at upper right corner
            c.fill(path.path(path.moveto(BS[0] - 1.5, BS[1]+0.5),
                path.lineto(BS[0]+0.5, BS[1]+0.5), path.lineto(BS[0]+0.5, BS[1] - 2),
                path.closepath()), [color.rgb(0.8, 0.8, 0.8)])
            c.text(BS[0]-0.1, BS[1]-0.5, title, [text.halign.boxcenter, text.halign.flushcenter, text.size(4)])
        self.canvases.append(c)

# some rendering helpers

def render_ant(c, x, y):
    #import Image
    print "render ant %s %s" % (x,y)
    #i = bitmap.jpegimage("ant.jpg")
    #i = Image.open('ant.jpg')
    #i.info['dpi'] = (2400, 2400) # required by pyx.bitmap
    #c.insert(bitmap.bitmap(x-0.45,y-0.45, i, compressmode='DCT'))
    c.insert(epsfile.epsfile(x-0.45, y-0.45, 'ant.eps'))

def render_obstacle(c, x, y):
    c.fill(path.rect(x - 0.25, y - 0.25, 0.5, 0.5))

def render_pheromone(c, x, y):
    c.fill(path.rect(x - 0.25, y - 0.25, 0.5, 0.5), [grey])

