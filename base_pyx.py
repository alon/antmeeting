""" To simplify base.py remove classes not related to it outside.
"""

class LineWidth(object):
    pass

class style(object):
    @staticmethod
    def linewidth(width):
        lw = LineWidth()
        lw.width = width
        return lw

class GridPyx(object):

    # Drawing helpers (pyx)

    def draw_home(self, c, i, j):
        x, y = j, self.size[0] - i
        s = 0.1
        d = 0.4
        lw = 0.05
        slw = style.linewidth(0.05)
        for px, py, dx, dy in [(x - d, y - d, 1, 1),
            (x + d, y - d, -1, 1), (x - d, y + d, 1, -1),
            (x + d, y + d, -1, -1)]:
            c.stroke(path.line(px - lw*dx/2, py, px + s*dx, py), [slw])
            c.stroke(path.line(px, py - lw*dy/2, px, py + s*dy), [slw])


