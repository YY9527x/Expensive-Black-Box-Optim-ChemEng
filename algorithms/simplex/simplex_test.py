import sys
sys.path.insert(1, 'test_functions')
import numpy as np 
from quadratic_constrained import * 
from rosenbrock_constrained import * 
from simplex_method import simplex_method

f = rosenbrock_f
g1 = rosenbrock_g1
g2 = rosenbrock_g2
d = 2
its = 50 
bounds = np.array([[-1.5,1.5],[-0.5,0.5]])
x0 = [0.5,0.5]

sol = simplex_method(f,x0,bounds,max_iter=its,constraints=[g1,g2])

print(sol) 