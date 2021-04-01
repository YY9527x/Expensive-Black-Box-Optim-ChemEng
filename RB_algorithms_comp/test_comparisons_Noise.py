# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 01:29:15 2021

@author: dv516
"""


import numpy as np
import pickle

import pyro
pyro.enable_validation(True)  # can help with debugging
pyro.set_rng_seed(1)

from algorithms.PyBobyqa_wrapped.Wrapper_for_pybobyqa import PyBobyqaWrapper
from algorithms.Bayesian_opt_Pyro.utilities_full import BayesOpt
from algorithms.nesterov_random.nesterov_random import nesterov_random
from algorithms.simplex.simplex_method import simplex_method
from algorithms.CUATRO.CUATRO import CUATRO
from algorithms.Finite_differences.Finite_differences import finite_Diff_Newton
from algorithms.Finite_differences.Finite_differences import Adam_optimizer
from algorithms.Finite_differences.Finite_differences import BFGS_optimizer
from algorithms.SQSnobfit_wrapped.Wrapper_for_SQSnobfit import SQSnobFitWrapper
from algorithms.DIRECT_wrapped.Wrapper_for_Direct import DIRECTWrapper

from test_functions import rosenbrock_constrained, quadratic_constrained

import matplotlib.pyplot as plt
import seaborn as sns

import itertools
import pandas as pd
import pickle

def average_from_list(solutions_list):
    N = len(solutions_list)
    f_best_all = np.zeros((N, 100))
    for i in range(N):
        f_best = np.array(solutions_list[i]['f_best_so_far'])
        x_ind = np.array(solutions_list[i]['samples_at_iteration'])
        for j in range(100):
            ind = np.where(x_ind <= j+1)
            if len(ind[0]) == 0:
                f_best_all[i, j] = f_best[0]
            else:
                f_best_all[i, j] = f_best[ind][-1]
    f_median = np.median(f_best_all, axis = 0)
    # f_av = np.average(f_best_all, axis = 0)
    # f_std = np.std(f_best_all, axis = 0)
    f_min = np.min(f_best_all, axis = 0)
    f_max = np.max(f_best_all, axis = 0)
    return f_best_all, f_median, f_min, f_max

def Problem_rosenbrock(x, noise_std, N_SAA):
    f_SAA = 0
    g_SAA1, g_SAA2 = - np.inf, -np.inf
    f1 = rosenbrock_constrained.rosenbrock_f
    g1 = rosenbrock_constrained.rosenbrock_g1
    g2 = rosenbrock_constrained.rosenbrock_g2
    for i in range(N_SAA):
        f_SAA += (f1(x) + np.random.normal(0, noise_std[0]))/N_SAA
        g_SAA1 = max(g1(x) + np.random.normal(0, noise_std[1]), g_SAA1)
        g_SAA2 = max(g2(x) + np.random.normal(0, noise_std[2]), g_SAA2)

    return f_SAA, [g_SAA1, g_SAA2]

n_noise = 6
noise_matrix = np.zeros((n_noise, 3))
for i in range(n_noise):
    noise_matrix[i] = np.array([0.05/3, 0.02/3, 0.02/3])*i

bounds = np.array([[-1.5,1.5],[-1.5,1.5]])
x0 = np.array([-0.5,1.5])

# max_f_eval = 100
max_f_eval = 50
max_it = 100

N_SAA = 2


N_samples = 20
RBnoise_list_pybbqa = []
RBconstraint_list_pybbqa = []
for i in range(n_noise):
    print('Iteration ', i, ' of Py-BOBYQA')
    best = []
    best_constr = []
    for j in range(N_samples):
        f = lambda x: Problem_rosenbrock(x, noise_matrix[i], N_SAA)
        sol = PyBobyqaWrapper().solve(f, x0, bounds=bounds.T, \
                                      maxfun= max_f_eval, constraints=2, \
                                      seek_global_minimum = True)
        best.append(sol['f_best_so_far'][-1])
        _, g = Problem_rosenbrock(sol['x_best_so_far'][-1], [0, 0, 0], N_SAA)
        best_constr.append(np.sum(np.maximum(g, 0)))
    RBnoise_list_pybbqa.append(best)
    RBconstraint_list_pybbqa.append(best_constr)

# N_SAA = 1
N_samples = 20
RBnoise_list_SQSF = []
RBconstraint_list_SQSF = []
for i in range(n_noise):
    print('Iteration ', i, ' of SQSnobfit')
    best = []
    best_constr = []
    for j in range(N_samples):
        f = lambda x: Problem_rosenbrock(x, noise_matrix[i], N_SAA)
        sol = SQSnobFitWrapper().solve(f, x0, bounds, \
                                   maxfun = max_f_eval, constraints=2)
        best.append(sol['f_best_so_far'][-1])
        _, g = Problem_rosenbrock(sol['x_best_so_far'][-1], [0, 0, 0], N_SAA)
        best_constr.append(np.sum(np.maximum(g, 0)))
    RBnoise_list_SQSF.append(best)
    RBconstraint_list_SQSF.append(best_constr)
    
# N_SAA = 1
N_samples = 20
RBnoise_list_DIRECT = []
RBconstraint_list_DIRECT = []
init_radius = 0.1
boundsDIR = np.array([[-1.5,1],[-1,1.5]])
for i in range(n_noise):
    print('Iteration ', i, ' of DIRECT')
    best = []
    best_constr = []
    for j in range(N_samples):
        f = lambda x: Problem_rosenbrock(x, noise_matrix[i], N_SAA)
        DIRECT_f = lambda x, grad: f(x)
        sol = DIRECTWrapper().solve(DIRECT_f, x0, boundsDIR, \
                                   maxfun = max_f_eval, constraints=2)
        best.append(sol['f_best_so_far'][-1])
        _, g = Problem_rosenbrock(sol['x_best_so_far'][-1], [0, 0, 0], N_SAA)
        best_constr.append(np.sum(np.maximum(g, 0)))
    RBnoise_list_DIRECT.append(best)
    RBconstraint_list_DIRECT.append(best_constr)
    
# N_SAA = 1
N_samples = 20
RBnoise_list_CUATROg = []
RBconstraint_list_CUATROg = []
init_radius = 2
for i in range(n_noise):
    print('Iteration ', i, ' of CUATRO_g')
    best = []
    best_constr = []
    for j in range(N_samples):
        f = lambda x: Problem_rosenbrock(x, noise_matrix[i], N_SAA)
        sol = CUATRO(f, x0, init_radius, bounds = bounds, max_f_eval = max_f_eval, \
                          N_min_samples = 15, tolerance = 1e-10,\
                          beta_red = 0.9, rnd = j, method = 'global', \
                          constr_handling = 'Discrimination')
        best.append(sol['f_best_so_far'][-1])
        _, g = Problem_rosenbrock(sol['x_best_so_far'][-1], [0, 0, 0], N_SAA)
        best_constr.append(np.sum(np.maximum(g, 0)))
    RBnoise_list_CUATROg.append(best)
    RBconstraint_list_CUATROg.append(best_constr)
    


noise = ['%.3f' % noise_matrix[i][0] for i in range(n_noise)]
noise_labels = [[noise[i]]*N_samples for i in range(n_noise)]


convergence = list(itertools.chain(*RBnoise_list_pybbqa)) + \
              list(itertools.chain(*RBnoise_list_SQSF)) + \
              list(itertools.chain(*RBnoise_list_DIRECT)) + \
              list(itertools.chain(*RBnoise_list_CUATROg))
              
constraints = list(itertools.chain(*RBconstraint_list_pybbqa)) + \
              list(itertools.chain(*RBconstraint_list_SQSF)) + \
              list(itertools.chain(*RBconstraint_list_DIRECT)) + \
              list(itertools.chain(*RBconstraint_list_CUATROg))
              
noise = list(itertools.chain(*noise_labels))*4
method = ['Py-BOBYQA']*int(len(noise)/4) + ['SQSnobfit']*int(len(noise)/4) + \
         ['DIRECT']*int(len(noise)/4) + ['CUATRO_g']*int(len(noise)/4)

data = {'Best function evaluation': convergence, \
        "Constraint violation": constraints, \
        "Noise standard deviation": noise, \
        'Method': method}
df = pd.DataFrame(data)


ax = sns.boxplot(x = "Noise standard deviation", y = "Best function evaluation", hue = "Method", data = df, palette = "muted")
plt.savefig('Publication plots format/SAA2feval50Convergence.svg', format = "svg")
# ax.set_ylim([0.1, 10])
# ax.set_yscale("log")
plt.clf()

ax = sns.boxplot(x = "Noise standard deviation", y = "Constraint violation", \
                    hue = "Method", data = df, palette = "muted", fliersize = 0)
ax = sns.stripplot(x = "Noise standard deviation", y = "Constraint violation", \
                    hue = "Method", data = df, palette = "muted", dodge = True)
plt.savefig('Publication plots format/SAA2feval50Constraints.svg', format = "svg")




