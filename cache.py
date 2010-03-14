import string
import json

totuple = lambda r1: (r1,) if not isinstance(r1, tuple) else r1

class Cacher:
    def __init__(self, filename):
        import sqlite3
        self._db = sqlite3.connect(filename)
        
    def has_table(self, table_name):
        try:
            self._db.execute('select * from %s limit 1' % table_name) # will kill you
            return True
        except:
            return False
    
    def table(self, table_name):
        return [tuple(json.loads(x) for x in s) for s in self._db.execute('select * from %s' % table_name).fetchall()]
    
    def insert(self, table_name, values):
        n = len(values[0]) if isinstance(values[0], tuple) else 1 
        self._db.executemany('insert into %s values (%s)' % (table_name, ','.join(['?']*n)), [tuple(json.dumps(x) for x in t) for t in values])
    
    def cached(self, f, n, params={}):
        assert(n > 0)
        table_name = 'cached_' + f.func_name
        if not self.has_table(table_name):
            r1 = totuple(f(**params))
            arity = len(r1)
            self._db.execute('create table %s (%s)' % (table_name, ','.join(string.lowercase[:arity])))
            self.insert(table_name, [r1])
            self._db.commit()
        results = self.table(table_name)
        new_results = []
        if n - len(results) > 0:
            r1 = f(**params)
            new_results.append(totuple(r1))
            for i in xrange(n - len(results) - 1):
                new_results.append(totuple(f(**params)))
            self.insert(table_name, new_results)
        self._db.commit()
        return results + new_results

def test():
    import os
    import random
    if os.path.exists('test.sqlite'):
        os.unlink('test.sqlite')
    def f(x):
        return x**2 + random.randint(0, 100)
    cache = Cacher('test.sqlite')
    n = 10
    v = cache.cached(f, n, params=dict(x=10))
    assert(len(v) == n)
    for i in xrange(n):
        assert(all(x1 == x2 for x1, x2 in zip(v, cache.cached(f, n, params=dict(x=10)))))
    v2 = cache.cached(f, n*2, params=dict(x=22))
    assert(len(v2) == n*2)
    assert(v[:n] == v2[:n])
    for i in xrange(n):
        assert(all(x1 == x2 for x1, x2 in zip(v2, cache.cached(f, n*2, params=dict(x=10)))))
    os.unlink('test.sqlite')
    v3 = cache.cached(f, n, params=dict(x=22))
    assert(v3 != v) # this could actually be the same, but <<1 chance.

if __name__ == '__main__':
    test()
    