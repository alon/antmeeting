""" mixin to avoid conditional imports for shedskin """


from render_to_pdf import render_ant

class MustMeetGui:
    """ mixin for MustMeet """
    def render_cell(self, cell, c, i, j):
        """ draw cell onto canvas """
        BOARD_SIZE = self.size
        # note that x and y are inverted, and that we put max_y - y to flip y
        x, y = j, BOARD_SIZE[0] - i
        grey = color.rgb(0.5,0.5,0.5)
        back_arrow = cell.get_back_arrow()
        cmds = []
        if cell.get_ant_sym() == ANT:
            # render the ant
            cmds.append(('ant',
                lambda c=c, x=x, y=y: render_ant(c, x, y)))
        if back_arrow == START: # draw H
            #c.text(j, BOARD_SIZE[1] - i, 'H')
            cmds.append(('home',
                lambda self=self, c=c, i=i, j=j: self.draw_home(
                    c, i, j)))
        elif back_arrow == OBSTACLE:
            assert(cell.get_ant_sym() == back_arrow)
            cmds.append(('obstacle',
                lambda c=c, x=x, y=y: c.fill(
                    path.rect(x - 0.25, y - 0.25, 0.5, 0.5))))
        else:
            back_arrow = cell.get_back_arrow()
            if back_arrow in [UP_SYM, DOWN_SYM, LEFT_SYM, RIGHT_SYM]:
                dx, dy = {UP_SYM: (0, -1), DOWN_SYM: (0, 1), LEFT_SYM: (-1, 0), RIGHT_SYM: (1, 0)}[back_arrow]
                cmds.append(('arrow',
                    lambda c=c, x=x, y=y, dx=dx, dy=dy: c.stroke(
                    path.line(x, y, x + dx, y - dy), [deco.earrow(),
                        style.linewidth(0.05)])))
        return cmds

