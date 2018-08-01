#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# =============================================================================
# File      : main.py -- Main file for the example
# Author    : Juergen Hackl <hackl@ibi.baug.ethz.ch>
# Creation  : 2018-08-01
# Time-stamp: <Mit 2018-08-01 13:36 juergen>
#
# Copyright (c) 2018 Juergen Hackl <hackl@ibi.baug.ethz.ch>
# =============================================================================
import os
import sys
import time
import csv
import numpy as np
from joblib import Parallel, delayed

# from setup import Setup
from scenario import Scenario
from path_diffusion_network import PathDiffusionNetwork_cnet

wk_dir = os.path.dirname(os.path.realpath('__file__'))
sys.path.insert(0, os.path.abspath(os.path.join(wk_dir, '../..')))


def generate_scenarios():
    """Function to generate multiple scenarios in parallel."""
    # list of scenarios (e.g. removed edges from the original network)
    scenarios = [None, 'E01']

    scenarios.extend(['N'+str(i+1).zfill(2) for i in range(1, 76)])

    # run analysis in parallel using all cpus
    Parallel(n_jobs=-1)(delayed(_scenario)(s) for s in scenarios)


def _scenario(e):
    """Function to generate a scenario."""
    Scenario(e, max_iter=100)


def print_probabilities(p):
    """Format the estimated probabilites."""
    print('-' * 80)
    print('pa = {:.3f}, pb = {:.3f}'.format(p[0], 1-p[0]))
    print('pc = {:.3f}, pd = {:.3f}, pe = {:.3f}'.format(
        p[1]/2, 1-p[1], p[1]/2))
    print('pf = {:.3f}, pg = {:.3f}'.format(p[2], 1-p[2]))
    print('ph = {:.3f}'.format(1))
    print('pi = {:.3f}, pj = {:.3f}'.format(p[3], 1-p[3]))
    print('pk = {:.3f}'.format(1))
    print('px = {:.3f}'.format(p[4]))
    print('-' * 80)


def main():
    """Main function to run the example code."""
    print('=' * 80)
    # node to remove
    node_to_remove = 'E01'
    # edges considered with length or above
    len_e = 3

    # Scenarios
    # =========
    # Base scenario
    S0 = Scenario()
    S0.paths.sort('fft')
    # Damaged scenario
    S1 = Scenario(node_to_remove)
    S1.paths.sort('fft')
    # Path diffusion model
    # ====================

    # Estimates
    start_time = time.time()
    EST = PathDiffusionNetwork_cnet(S0.network, S0.paths, n_edges=len_e)
    elapsed_time = time.time() - start_time
    print('Create network: ', elapsed_time)

    start_time = time.time()
    EST.deactivate_path(node_to_remove)
    elapsed_time = time.time() - start_time
    print('Deactivate path: ', elapsed_time)

    start_time = time.time()
    EST.assign_probabilities()
    elapsed_time = time.time() - start_time
    print('Assign probabilities: ', elapsed_time)

    start_time = time.time()
    EST.run_diffusion()
    elapsed_time = time.time() - start_time
    print('Run diffusion: ', elapsed_time)

    EST.summary()
    print('---')

    # Observations
    OBS = PathDiffusionNetwork_cnet(S1.network, S1.paths, n_edges=len_e)
    OBS.assign_probabilities()
    OBS.summary()

    V_est = EST.volume(original=True)
    V_obs = OBS.volume(original=True)

    error = np.sum((V_obs-V_est)**2)
    abs_error = V_obs-V_est
    rel_error = np.abs(V_obs-V_est) / V_obs

    # for i in range(len(V_est)):
    #     print(V_est[i], V_obs[i], abs_error[i], rel_error[i])

    print('---')
    print(error)
    print('---')
    print(np.max(rel_error))
    print(np.min(rel_error))
    print(np.mean(rel_error))
    print(np.std(rel_error))
    print('---')
    print(np.max(abs_error))
    print(np.min(abs_error))
    print(np.mean(abs_error))
    print(np.std(abs_error))

    print('=' * 80)


def _estimate(EST, V_obs, p):
    """Function to estimate the errors."""
    EST.assign_probabilities(p)
    EST.run_diffusion()
    V_est = EST.volume()
    error = [np.sum((V_obs-V_est)**2)]
    error.extend(p)
    error.extend(V_est.tolist())
    return error


def estimate(node_to_remove='E01', number_of_simulations=1000, len_e=3):
    """Estimate the parameters of the transition matrices."""
    print('=' * 80)
    S0 = Scenario()
    S0.paths.sort('fft')
    S1 = Scenario(node_to_remove)
    S1.paths.sort('fft')

    print('-' * 80)

    # Estimates
    start_time = time.time()
    EST = PathDiffusionNetwork_cnet(S0.network, S0.paths, n_edges=len_e)
    elapsed_time = time.time() - start_time
    print('Create network: ', elapsed_time)

    start_time = time.time()
    EST.deactivate_path(node_to_remove)
    elapsed_time = time.time() - start_time
    print('Deactivate path: ', elapsed_time)

    # Observations
    OBS = PathDiffusionNetwork_cnet(S1.network, S1.paths, n_edges=len_e)
    OBS.assign_probabilities()

    V_obs = OBS.volume(original=True)

    print('-' * 80)

    r = np.random.rand(number_of_simulations, 5)

    start_time = time.time()
    sim_results = Parallel(n_jobs=7)(
        delayed(_estimate)(EST, V_obs, p) for p in r)

    elapsed_time = time.time() - start_time
    print('Run time per simulation: {:.3f}'.format(
        elapsed_time/number_of_simulations))
    print('Run time  in total: {:.3f}'.format(elapsed_time))

    sim_results.sort()

    filename = './temp/estimates.csv'
    with open(filename, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(sim_results)

    print('-' * 80)

    sqe_1 = sim_results[0][0]
    sqe_2 = sim_results[1][0]
    p = np.array(sim_results[0][1:6])
    V_est = np.array(sim_results[0][6:])

#    error = np.sum((V_obs-V_est)**2)
    abs_error = V_obs-V_est
    rel_error = np.abs(V_obs-V_est) / V_obs

    print('squar error: {:.3f} ({:.3f})'.format(sqe_1, sqe_2))
    print('max abs error: {:.3f}'.format(np.max(abs_error)))
    print('min abs error: {:.3f}'.format(np.min(abs_error)))
    print('mea abs error: {:.3f}'.format(np.mean(abs_error)))
    print('std abs error: {:.3f}'.format(np.std(abs_error)))

    print('max rel error: {:.2f} %'.format(np.max(rel_error)*100))
    print('min rel error: {:.2f} %'.format(np.min(rel_error)*100))
    print('mea rel error: {:.2f} %'.format(np.mean(rel_error)*100))
    print('std rel error: {:.2f} %'.format(np.std(rel_error)*100))

    print_probabilities(p)
    pass


if __name__ == '__main__':
    generate_scenarios()
    # main()
    # estimate()

# =============================================================================
# eof
#
# Local Variables:
# mode: python
# mode: linum
# mode: auto-fill
# fill-column: 80
# End:
