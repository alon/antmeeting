
# UGLY HACK
def juxta(x,y):
    return 11-y,x

# Runs definition - (constructor, output pdf name, parameters)

defaults = {
        "board_size" : (12,  12), #number of rows (y), number of cols (x)
        "ant_locations" : [(7, 7), (2, 2)],
        "steps" : 680
    }

def_board_size = defaults['board_size']

# noa vs coa world

noa_empty_world_1 = """
            
            
            
    1       
            
            
            
            
       2    
            
            
            
""".split("\n")[1:-1] # remove empty lines from start and finish


noa_vs_coa_world = """
            
            
            
     1      
            
     ***    
            
            
       2    
            
            
            
""".split("\n")[1:-1] # remove empty lines from start and finish


# convex world for coa

non_convex_world = """
           *
           *
           *
           *
           *
  *****    *
  *   *    *
  * 1 *    *
  *     2  *
  *****    *
           *
           *
""".split("\n")[1:-1] # remove empty lines from start and finish

infinite_world = """
          * 
          * 
          * 
          * 
          * 
          * 
 *****   2* 
 *   *    * 
 *   *    * 
 *        * 
 *****   1* 
          * 
""".split("\n")[1:-1] # remove empty lines from start and finish

goa_example_world = """
****      * 
*  *      * 
*      **** 
*      *  * 
*    ***2 * 
          * 
 *****    * 
 * 1 *    * 
 *   *    * 
 *        * 
 *****    * 
          * 
""".split("\n")[1:-1] # remove empty lines from start and finish


coa_runs = [
        (COARun, 'COA_no_obstacles', {
            "render_steps" : [0, 50]
        }),
]

goa_runs = [
        (GOARun, 'GOA_no_obstacles', {}),

        (GOARun, 'GOA_step_by_step', {
             "obstacles" : non_convex_world
            }),
]

coa_vs_goa = [
        (COARun, 'COA_failure', {
            "obstacles" : non_convex_world,
            "steps" : 37
        }),
        (COARun, 'COA_infinite', {
            "obstacles" : infinite_world,
            "steps" : 6
        }),
        (GOARun, 'GOA_success', {
            "obstacles" : non_convex_world
            }),
        (GOARun, 'GOA_example_world', {
            "obstacles" : goa_example_world
            }),
        (GOARun, 'GOA_no_obstacles', {
            "steps" : 120,
            }),
]

goa_steps = [
        (GOARun, 'GOA_no_obstacles', {
            "steps" : 14,
            "draw_slide_title" : True,
            #render_steps = range(14),
            "board_size" : (4,  4), # number of rows (y) - 1, number of cols (x) - 1
            "ant_locations" : [(2, 2)]
            })
]

slides = [
    #('NOA_meetings', noa_meetings, {}),
    #('NOA_vs_COA', noa_vs_coa, {}),
    #('COA_vs_GOA', coa_vs_goa, {}),

    # Slides used for second version of article:

    #('noa_vs_coa', noa_vs_coa + coa_vs_goa[:2], {'num_in_row':2}),
    #('coa_vs_goa', coa_vs_goa[4:] + coa_vs_goa[2:4], {'num_in_row':2}),
    ('GOA_Steps', goa_steps, {'num_in_row':4, 'with_numbering':False}),
]

def randpoint(size):
    return map(lambda x: random.randint(2, x-3), size)

class GridIsObst:
    def __init__(self, grid):
        self.grid = grid

    def is_obst(self, grid, (x, y)):
        return grid.grid[x][y].is_obstacle()

def randants(run):
    grid = run.grid
    ants = run.ants
    locs = [randpoint(grid.size) for x in xrange(len(ants))]
    is_obst = GridIsObst(grid).is_obst
    while any(map(is_obst, locs)):
        locs = [randpoint(grid.size) for x in xrange(len(ants))]
    run.update_ant_locations(locs)

if __name__ == '__main__':
    #create_pdf_slides(slides)
    multirun()

