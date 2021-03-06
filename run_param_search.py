#!/usr/bin/env python3
""" NARS benchmarking using hyperopt

This module uses hyperopt to explore a user defined hyperparameter search space for NARS
Benchmarking is done by performing multiple runs of NARS and taking the average performance defined by the optimization objective
All configurations are done through config.json
For help and details, refer to README.md

"""

__authors__ = "Yuhong Sun"
__license__ = "MIT License"

import subprocess
import json
import time
import signal
import multiprocessing as mp
from statistics import mean
from hyperopt import hp, fmin, tpe
import objectives


# Read config.json for initial setup, for details on the fields see README.md
with open('config.json', 'r') as config_json:
    config = json.load(config_json)
NARS_FILES = config['NARS input files']
PARAMS = config['NARS parameters']
DEBUG = (config['debug'] == "True" or config['debug'] == "True")
OBJECTIVE = config['optimization objective']
FAILURE_PENALTY = config['failure penalty']
HYPEROPT_ITERS = config['Hyperopt iterations']
RUNS_PER_ITER = config['NARS runs per iteration']
THREADS = config['cpu threads']
NARS_TO = config['NARS timeout']
BATCH_TO = config['batch timeout']
EXACT_TV = (config['require exact truth value'] == "True" or config['require exact truth value'] == "true")

print("Running hyperparameter search with goal: " + OBJECTIVE + "\n")

# Single run if running in debug mode
if DEBUG:
    HYPEROPT_ITERS = RUNS_PER_ITER = THREADS = 1
    NARS_FILES = [NARS_FILES[0]]

def extract_targets(nars_file):
    """ Extract the target statements that NARS is suppose to generate given the input file

    Args:
        nars_file: String for the file path of the Narsese file to benchmark
    Returns:
        List of strings which should appear in the NARS output when it digests nars_file
    """
    targets = []
    # Target statements are expected to defined in Narsese file starting with the following pattern
    target_stamp = "\'\'outputMustContain(\'"
    with open(nars_file, "r") as narsese:
        for line in narsese:
            if target_stamp in line:
                if EXACT_TV: targets.append(line.split(target_stamp)[1][:-3])
                else: targets.append(line.split(target_stamp)[1].split("%")[0])
    if DEBUG:
        print("\n\tFound Target Statements: ")
        [print("\t\t" + target) for target in targets]
        print("\n")
        time.sleep(1)
    return targets


def get_space():
    """ Create a parameter space taken by hyperopt
    The dimensions of the space is entirely defined by config.json and sampling is later provided by hyperopt

    Returns:
        dictionary with the keys as the named dimensions and values as hyperopt hp pointers
    """
    space = {}
    for param in PARAMS:
        # 3 value param expected to follow format: [name, lowerbound, upperbound]
        if type(param[1]) == float or type(param[2]) == float:
            space[param[0]] = hp.uniform(param[0], param[1], param[2])
        elif type(param[1]) == int or type(param[2]) == int:
            space[param[0]] = hp.quniform(param[0], param[1], param[2], 1)
        # 2 value param expected to follow format: [name, True/False]
        elif len(param) == 2:
            space[param[0]] = hp.quniform(param[0], 0, 1, 1)
    return space


def run_nars(args_file_tuple):
    """ Run a single instance of NARS as a separate java subprocess and calls objective function
    Runs NARS until all target statements are derived by the reasoner or a user specified timeout is reached
    Calls user specified objective function if all target statements are successfully derived.

    Args:
        args_file_tuple: a list of two arguments combined for multiprocessing pool.map
                         unpacks to 1.) list of parameters for the NARS java wrapper and 2.) a Narsese file path
    Return:
        A loss value for this particular run of NARS
    """
    # Expand the arguments to parameters for NARS and a Narsese file path
    args = args_file_tuple[0]
    nars_file = args_file_tuple[1]

    # Extract target statements
    targets = extract_targets(nars_file)

    # Build up a command string to run as a separate java NARS process
    process_cmd = ['java', '-cp', '.:*', 'run_nars', nars_file]
    for key in args:
        flag = '-' + str(key)
        value = str(args[key])
        if args[key].is_integer():
            value = str(int(args[key]))
        process_cmd.append(flag)
        process_cmd.append(value)
    if DEBUG: print("\nExecuting: " + str(process_cmd) + "\n")

    # Execute NARS in shell mode and capture output
    process = subprocess.Popen(process_cmd, stdout=subprocess.PIPE)
    fd = process.stdout

    # Start timing NARS
    start_time = time.time()

    # Run NARS until all target statements are found or the timeout is reached
    found_targets = []
    content = []
    stop_time = time.time() + NARS_TO
    while time.time() < stop_time and len(found_targets) < len(targets):
        newline = fd.readline().decode('utf-8')
        content.append(newline)
        for target in targets:
            if (target in newline) and (target not in found_targets) and ("ECHO:" not in newline) and ("IN:" not in newline):
                found_targets.append(target)
                if DEBUG: print("Found target line:\n" + newline)

    # Read a few more lines for context following last target (such as DEBUG: outputs)
    for _ in range(10):
        content.append(fd.readline().decode('utf-8'))

    # Kill the running NARS as it's no longer useful and get the time
    process.terminate()
    nars_run_time = time.time() - start_time

    # Return penalty from config.json if not all target statements were output by NARS
    if len(found_targets) < len(targets):
        if DEBUG:
            print("NARS failed to generate all require target statements")
            print("\tMissing Targets:")
            for target in targets:
                if target not in found_targets:
                    print("\t\t" + target)
        return FAILURE_PENALTY

    # Select one of the objective functions defined in objectives.py
    objective_func = getattr(objectives, OBJECTIVE, None)
    if objective_func:
        return mean([objective_func(target, content, nars_run_time, DEBUG, FAILURE_PENALTY) for target in found_targets])
    else:
        print("\n\n\n\nFatal: objective function is not found\n       Please select valid objective in config.json")
    return FAILURE_PENALTY


def signal_handler(signal, frame):
    """ Handles edge case where a spawned process hangs
    Occurs very rarely when spawning parallel subprocesses with subprocess.pool
    Caller simply abandons the batch and retries

    Args:
        signal: received signal
        frame: current stack frame
    """
    # No additional handling required except a message as caller simply retries batch
    raise Exception("\t\tBatch timed out, retrying")


def parallelized_objective(args):
    """ Uses subprocess to create parallel instances of NARS and run objective functions in parallel

    Args:
        args: hyperopt generated values for each named dimension to be translated into NARS parameters
    """
    print("Iteration using parameters:\n" + str(args))
    losses = []
    # Handle each Narsese file in sequence
    for nars_file in NARS_FILES:
        print("\n\tBenchmarking file: " + nars_file.split("/")[-1])
        file_loss = []
        # Created batches for each file
        for _ in range(round(RUNS_PER_ITER / THREADS)):
            success = False
            while not success:
                # Each batch is given a maximum time before it is assumed a worker hung
                signal.alarm(BATCH_TO)
                try:
                    with mp.Pool(THREADS) as p:
                        batch = p.map(run_nars, [(args, nars_file)] * THREADS)
                        print("\t\tBatch results: " + str(batch))
                    losses += batch
                    file_loss += batch
                    success = True
                # If not successful, print a message and try again
                except Exception as e:
                    print(str(e))
        print("\tFile average loss: " + str(mean(file_loss)))

    # Average the losses across all runs of NARS
    loss = mean(losses)
    print("\nHyperopt Iteration Loss: " + str(loss) + "\n\n")
    return loss


# =====================
# Execution begins here
# =====================

# In case subprocess pool hangs
signal.signal(signal.SIGALRM, signal_handler)

# Define a search space based on configurations in config.json
hyperopt_search_space = get_space()

# Run hyperopt and keep the best parameters
best = fmin(parallelized_objective, hyperopt_search_space, algo=tpe.suggest, max_evals=HYPEROPT_ITERS)
print(best)
