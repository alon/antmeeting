from constants import U,R,D,L,X,S,M, ANT_SYMBOL

# state, symbols -> nextstate, action, written
base_meet = [
("""
   
   
   
""", U, X),
("""
   
   
 X 
""", R, X),
("""
   
X  
X  
""", D, X),
("""
XX 
X  
   
""", D, X),
("""
XX 
   
   
""", L, X),
("""
 XX
  X
   
""", L, X),
("""
  X
  X
   
""", U, X),
("""
  X
  X
 XX
""", U, X),
("""
   
  X
 XX
""", U, X),
("""
   
   
 XX
""", R, X),
("""
   
X  
XXX
""", R, X),
("""
   
X  
XX 
""", R, X),
("""
   
X  
X  
""", D, X),
("""
XX 
X  
X  
""", D, X),
("""
XX 
X  
X  
""", D, X),
("""
XX 
X  
   
""", D, X),
("""
XX 
   
   
""", L, X),
("""
XXX
  X
   
""", L, X),
("""
XXX
  X
   
""", L, X),
("""
 XX
  X
   
""", L, X),
("""
  X
  X
 XX
""", U, X),
("""
  X
  X
 XX
""", U, X),
("""
  X
  X
 XX
""", U, X),
("""
   
X  
XXX
""", R, X),
("""
   
X  
XXX
""", R, X),
("""
XXX
  X
   
""", L, X),
("""
   
X  
XXX
""", R, X),
("""
XX 
X  
X  
""", D, X),
# These are the states of two Ants
("""
XX 
   
X  
""", S, X),
("""
  X
X  
XXX
""", R, X),
("""
 XX
  X
X  
""", S, X),
("""
XX 
   
XX 
""", S, X),
("""
  X
   
 XX
""", R, X),
("""
  X
  X
X  
""", S, X),
("""
  X
X  
X  
""", S, X),
("""
  X
   
 X 
""", S, X),
("""
 X 
   
 X 
""", S, X),
("""
  X
X X
X  
""", S, X),
("""
X X
X X
X  
""", U, X),
("""
  X
X X
XXX
""", S, X),
("""
   
X X
X X
""", S, X),
("""
X X
  X
   
""", U, X),
("""
X X
X X
   
""", U, X),
("""
X X
X X
XXX
""", U, X),
("""
   
X X
XXX
""", S, X),
("""
   
X  
X X
""", S, X),
("""
X X
  X
 XX
""", U, X),
("""
X  
X X
 XX
""", S, X),
("""
XX 
X  
  X
""", S, X),
("""
X  
   
 X 
""", S, X),
("""
X X
X X
 XX
""", U, X),
("""
X  
X X
XXX
""", S, X),
("""
XX 
   
 XX
""", S, X),
("""
XX 
   
  X
""", S, X),
("""
X  
  X
 XX
""", S, X),
("""
 XX
   
 XX
""", R, X),
("""
XXX
X  
XXX
""", R, X),
("""
 XX
X  
XXX
""", R, X),
("""
XXX
   
 XX
""", R, X),
]

def binary(b):
    ret = []
    num = 8
    while b > 0:
        ret.append((b%2 == 0 and 'X') or ' ')
        b >>= 1
        num -= 1
    ret.extend(['X']*num)
    return ret

for x in xrange(3):
    for y in xrange(3):
        if x == 1 and y == 1: continue
        for b in xrange(256):
            bin = binary(b)
            symbols = bin[:3] + ['\n'] + bin[3:4] + [' '] + bin[4:5] + ['\n'] + bin[5:] + ['\n']
            symbols[y*4+x] = ANT_SYMBOL
            symbols = ''.join(symbols)
            base_meet.append((symbols, M, None))

