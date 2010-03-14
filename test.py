def t(x):
 f = open('../a2/' + x, 'rb') 
 print repr(f.read(500))
 f.close()
 f = open(x, 'rb')
 print repr(f.read(500))
 f.close()
