import subprocess
import re
import os
import json
import time
import signal
import multiprocessing as mp
from statistics import mean 
from hyperopt import hp, fmin, tpe, space_eval
import objectives

# Run initial setup when this file is imported
with open('config.json', 'r') as config_json:
    config = json.load(config_json)

nars_files = config['NARS input files']
params = config['NARS parameters']
debug = (config['debug'] == "True" or config['debug'] == "True")
objective_func = config['optimization objective']
failure_penalty = config['failure penalty']
hyperopt_iters = config['hyperopt iterations']
runs_per_iter = config['NARS runs per iteration']
cores = config['cpu cores']
NARS_TO = config['NARS timeout']
batch_TO = config['batch timeout']
exact_TV = (config['require exact truth value'] == "True" or config['require exact truth value'] == "true" )

if failure_penalty < 10000 and objective_func == "cycles":
    print("Consider using a higher failure penalty (at least 10000) for optimization objective = cycles")
    time.sleep(2)


# Extract the target statements given an input Narsese file
def extract_targets(nars_file):
    if debug: print("\tProcessing NARS input file: " + nars_file + "\n")
    targets = []
    # Target statements expected to begin with the following pattern in the Narsese file.
    target_stamp = "\'\'outputMustContain(\'"
    with open(nars_file, "r") as narsese:
        for line in narsese:
            if target_stamp in line:
                if exact_TV: targets.append(line.split(target_stamp)[1][:-3])
                else: targets.append(line.split(target_stamp)[1].split("%")[0])
    if debug:       
        print("\tFound Target Statements: ")
        [print("\t" + target) for target in targets]
        print("\n")
        time.sleep(1)
    return targets


def get_space():
    space = {}
    # All params expected to follow format: [name, lowerbound, upperbound] or [name, True/False] 
    for param in params:
        if type(param[1]) == float or type(param[2]) == float:
            space[param[0]] = hp.uniform(param[0], param[1], param[2])
        elif type(param[1]) == int or type(param[2]) == int:
            space[param[0]] = hp.quniform(param[0], param[1], param[2], 1)
        elif len(param) == 2:
            space[param[0]] = hp.quniform(param[0], 0, 1, 1)
    return space


def objective(args_file_tuple):
    args = args_file_tuple[0]
    nars_file = args_file_tuple[1]
    targets = extract_targets(nars_file)
    process_cmd = ['java', '-cp', '.:opennars-3.0.4-SNAPSHOT.jar', 'run_nars', nars_file]
    for key in args:
        flag = '-' + str(key)
        value = str(args[key])
        if args[key].is_integer():
            value = str(int(args[key]))
        process_cmd.append(flag)
        process_cmd.append(value)
    if debug: print("\tExecuting: " + str(process_cmd))
    
    # Execute NARS in shell mode and capture output
    process = subprocess.Popen(process_cmd, stdout=subprocess.PIPE)
    fd = process.stdout

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
                if debug: print("Found target line: " + newline)

    # Read a few more lines for context following last target (such as DEBUG: outputs)
    for i in range(10):
        content.append(fd.readline().decode('utf-8'))
    
    # Kill the running NARS as it's no longer useful
    process.terminate()
    
    # Return penalty if not all target statements were output by NARS
    if len(found_targets) < len(targets):
        if debug: 
            print("NARS failed to generate all require target statements")
            print("Missing Targets:")
            for target in targets:
                if target not in found_targets:
                    print(target)
        return failure_penalty
    
    # Trim off truth value if specified in config.json
    if not exact_TV:
        found_targets = [target.split(" %")[0] for target in found_targets]

    # Select one of the objectives defined in objectives.py
    if objective_func == "chain_length":
        return mean([objectives.chain_length(target, content) for target in found_targets])
    elif objective_func == "num_cycles":
        return mean([objectives.num_cycles(target, content) for target in found_targets])
    else:
        print("objective function is not found, please select valid objective in config.json")
    return failure_penalty


# In case a thread dies
def signal_handler(signum, frame):
    raise Exception("\t\tBatch timed out, retrying")


def parallelized_objective(args):
    print("Iteration using parameters:\n" + str(args))
    losses = []
    for nars_file in nars_files:
        print("\n\tBenchmarking file: " + nars_file)
        for it in range(round(runs_per_iter / cores)):
            success = False
            while not success:
                # Each batch is given a maximum time before it is assumed a worker hung
                signal.alarm(batch_TO)
                try:
                    with mp.Pool(cores) as p:
                        batch = p.map(objective, [(args, nars_file)] * cores)
                        print("\t\tBatch results: " + str(batch))
                    losses += batch
                    success = True
                # If not successful, print a message and try again
                except Exception as e:
                        print(str(e))

    loss = mean(losses)
    print("Hyperopt Iteration Loss: " + str(loss) + "\n\n")
    return loss


# =====================
# Execution begins here
# =====================

# In case subprocess pool hangs
signal.signal(signal.SIGALRM, signal_handler)

hyperopt_search_space = get_space()

best = fmin(parallelized_objective, hyperopt_search_space, algo=tpe.suggest, max_evals=hyperopt_iters)

print(best)
