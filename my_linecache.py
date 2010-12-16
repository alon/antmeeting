cache = {}

def getlines(filename):
    if filename not in cache:
        fd = open(filename)
        lines = fd.readlines()
        cache[filename] = lines
        fd.close()
    return cache[filename]
