from numarray import *

nan = float('nan')

def different_size_binary_operation(oper):
    """Returns an operation which will work on different sized 1-d arrays"""
    def newoper(x, y):
        try:
            lx = len(x)
            ly = len(y)
        except TypeError:  
            # one of the two is a scalar
            return oper(x, y)

        if (hasattr(x, 'shape') and len(x.shape) == 0) or (hasattr(y, 'shape') and len(y.shape) == 0):
            # one of the two is a zero-dimensional array
            return oper(x, y)

        length = max(lx, ly)
        x = concatenate([x, array([nan]*(length-lx))])
        y = concatenate([y, array([nan]*(length-ly))])
        return oper(x, y)
    return newoper

# XXX: problem: sin(x) + sin(y) fails!

def wrap(func):
    def wrapped(x):
        return VarArray(func(x))
    return wrapped

# setup operations

d = {}
for k, u in [(k, f) for k, f in dict(globals()).items() if type(f) == ufunc._BinaryUFunc]:
    d[k] = different_size_binary_operation(u)

#for k, u in [(k, f) for k, f in dict(globals()).items() if type(f) == ufunc._UnaryUFunc]:
#    d[k] = wrap(u)


globals().update(d)
    

## simple arithmetic operators 
#add = different_size_binary_operation(add)
#subtract = different_size_binary_operation(subtract)
#multiply = different_size_binary_operation(multiply)
#divide = different_size_binary_operation(divide)
#power = different_size_binary_operation(power)

## comparison operators
#not_equal = different_size_binary_operation(not_equal)
#less = different_size_binary_operation(less)
#less_equal = different_size_binary_operation(less_equal)
#greater = different_size_binary_operation(greater)
#greater_equal = different_size_binary_operation(greater_equal)

class VarArray(numarraycore.NumArray):
    def __add__(self, other): return add(self, asarray(other)) 
    __radd__ = __add__
    def __sub__(self, other): return subtract(self, asarray(other)) 
    def __rsub__(self, other): return subtract(asarray(other), self) 
    def __mul__(self, other): return multiply(self, asarray(other))
    __rmul__ = __mul__
    def __div__(self, other): return divide(self, asarray(other)) 
    def __rdiv__(self, other): return divide(asarray(other), self) 
    def __pow__(self,other): return power(self, asarray(other)) 

#    def __eq__(self,other): return equal(self,other) 
    def __ne__(self,other): return not_equal(self,asarray(other)) 
    def __lt__(self,other): return less(self,asarray(other)) 
    def __le__(self,other): return less_equal(self,asarray(other)) 
    def __gt__(self,other): return greater(self,asarray(other)) 
    def __ge__(self,other): return greater_equal(self,asarray(other))





class Column(UsesOpPriority):
    op_priority = 1.0   # NumArray + MA --> MA
    def __init__(self, worksheet, n):
        self.worksheet, self.n = worksheet, n

    def get_data(self):
        return self.worksheet.data[self.n]
    data = property(get_data)

    def __getitem__(self, item):
        return self.worksheet.data[self.n][item]

    def __setitem__(self, item, value):
        self.data[item] = value

    def __str__(self): return str(self.data)
    def __repr__(self): return repr(self.data)

    def __len__(self): return len(self.data)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.data, attr)

    def __add__(self, other): return add(self.data, asarray(other)) 
    __radd__ = __add__
    def __sub__(self, other): return subtract(self.data, asarray(other)) 
    def __rsub__(self, other): return subtract(asarray(other), self.data) 
    def __mul__(self, other): return multiply(self.data, asarray(other))
    __rmul__ = __mul__
    def __div__(self, other): return divide(self.data, asarray(other)) 
    def __rdiv__(self, other): return divide(asarray(other), self.data) 
    def __pow__(self,other): return power(self.data, asarray(other)) 

#    def __eq__(self,other): return equal(self,other) 
    def __ne__(self,other): return not_equal(self.data,asarray(other)) 
    def __lt__(self,other): return less(self.data,asarray(other)) 
    def __le__(self,other): return less_equal(self.data,asarray(other)) 
    def __gt__(self,other): return greater(self.data,asarray(other)) 
    def __ge__(self,other): return greater_equal(self.data,asarray(other))


class Worksheet(object):
    def __init__(self):
        self.data = array(shape=(0,0), type=Float64)
        self.columns = []
    
    def get_ncolumns(self):
        return self.data.shape[0]
    ncolumns = property(get_ncolumns)

    def get_nrows(self):
        return self.data.shape[1]
    nrows = property(get_nrows)

    def get_as_rows(self):
        v = view(self)
        v.swapaxes(0,1)
        return v
    as_rows = property(get_as_rows)

    def add_column(self, name):
        self.data = concatenate([ self.data, [[nan]*self.nrows] ])
        self.columns.append(name)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        elif name in self.columns:
            return Column(self, self.columns.index(name))

    def __str__(self):
        s = "Worksheet:"
        for i,c in enumerate(self.columns):
            s += '\n   ' + c + ": " + str(self.data[i])
        return s

    def _extend(self, rows):
        if rows > self.nrows:
            self.data.swapaxes(0,1)
            # careful, nrows are ncols and ncols are nrows
            self.data = concatenate([ self.data, [[nan]*self.nrows]*(rows-self.ncolumns) ])
            self.data.swapaxes(0,1)

    def __getitem__(self, key):
        return None
        

w = Worksheet()
w.add_column('A')
w.add_column('V')
w._extend(3)
w._extend(5)
w.add_column('Star')

w[3]
w[3,3]
w[:,3]
s = w.Star
s[4] = 13
w.A[4] = 23
print w.Star
print w.Star + array([1,2,3,4,5,6,7,])
print sin(w.Star) + sin(array([1,2,3,4,5,6,7,]))
