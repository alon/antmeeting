"""
keep all the rendering functions in one place

currently:
render to ascii
render to pdf (requires pyx)
"""

__all__ = ['Renderer', 'AsciiRenderer', 'render_factories']

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
