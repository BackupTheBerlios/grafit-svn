def linear(x, a, b):
    return a*x + b

linear.name = 'Linear'
linear.initial_values = [1., 0.]
linear.tex = r'f(x) = \alpha x+\beta'

functions = [linear]
