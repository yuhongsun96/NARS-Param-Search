import subprocess
import re
import os
import time
import signal
import multiprocessing as mp
from statistics import mean 
from hyperopt import hp, fmin, tpe, space_eval

# Nars input file
nars_file = "toothbrush.nal"
# Turn on debug, only runs 1 hyperopt iteration with a single trial
debug = False
# Number of iterations of hyperopt
num_evals = 40
# Timeout limit in seconds for NARS to conclude all target statements
timeout = 10
# Failure penalty in case NARS fails to conclude all target statements
penalty_failed = 100
# Number of trials per hyperopt iteration (since NARS is nondeterministic)
trials = 40 # Optimally should be multiple of cores (see below)
# Cores available for parallelizing
cores = 4
# Objective, choose "chain_length" for minimizing inference chain length or "cycles" for minimizing number of cycles until target statements are derived
optimization_objective = "chain_length"
# Batch timeout, in case multiprocess pool hangs
batch_TO = 60

# Setup
target_stamp = "\'\'outputMustContain(\'"
if debug: num_evals = 1
debug_str_1 = "DEBUG: Parent Belief\t"
debug_str_2 = "DEBUG: Parent Task\t"
regex_null = re.compile(r'\s?null\s?')
if penalty_failed < 10000 and optimization_objective == "cycles":
    print("Consider using a higher penalty_failed (at least 10000) for optimization_objective = cycles")
    time.sleep(2)
targets = []
print("Using NARS input file: " + nars_file + "\n")
with open(nars_file, "r") as narsese:
    for line in narsese:
        if target_stamp in line:
            targets.append(line.split(target_stamp)[1][:-3])

print("Found Target Statements: ")
[print("\t" + target) for target in targets]
print("\n")
time.sleep(1)

# Get the longest path through ancestry tree of statement
def longest_ancestry(statement, depth, text):
    # Iterate text to find target statement and retrieve its parent statements (next 2 lines)
    if debug: print("target: " + statement)
    keep = 0
    parent1 = parent2 = None
    last_line = None
    for ind, line in enumerate(text):
        if keep == 2:
            parent1 = line
            keep = 1
            continue
        elif keep == 1:
            parent2 = line
            break
        elif statement in line and "OUT: " in line:
            keep = 2
            last_line = ind
    
    # Failsafe, in case target statement is not found
    if parent1 == None or parent2 == None:
        print("Unable to find parents")
        return penalty_failed

    if debug: print("parent 1: " + parent1)
    if debug and regex_null.search(parent1): print("Terminal case parent 1")
    if debug: print("parent 2: " + parent2)
    if debug and regex_null.search(parent2): print("Terminal case parent 2")

    # Failsafe, the two lines following the OUT: line with target should be the 2 Debug parent statements
    if debug_str_1 not in parent1 or debug_str_2 not in parent2:
        print("Statement found in:\n" + text[last_line])
        print("Parent 1:\n" + parent1)
        print("Parent 2:\n" + parent2)
        print("Unexpected parent string")
        return penalty_failed

    # Trim off label and truth value
    parent1 = parent1.split(debug_str_1)[1].split(" %")[0]
    parent2 = parent2.split(debug_str_2)[1].split(" %")[0]

    # If parent is null, that branch is done, else call longest ancestry again
    len1 = depth + 1 if regex_null.search(parent1) else longest_ancestry(parent1, depth + 1, text[:ind])
    len2 = depth + 1 if regex_null.search(parent2) else longest_ancestry(parent2, depth + 1, text[:ind])

    #Return longest path of ancestry tree
    return max(len1, len2)


# Objective function used for Hyperopt
def objective(args):
    # Specify NARS Parameters
    process_cmd = ['java', '-cp', '.:opennars-3.0.4-SNAPSHOT.jar', 'run_nars', \
        str(args['DERIVATION_PRIORITY_LEAK']), \
        str(int(args['VARIABLE_INTRODUCTION_COMBINATIONS_MAX'])), \
        str(int(args['SEQUENCE_BAG_ATTEMPTS'])), \
        str(int(args['TERM_LINK_MAX_MATCHED']))]
    if debug: print("Executing: " + str(process_cmd))

    # Execute NARS in shell mode and capture output
    process = subprocess.Popen(process_cmd, stdout=subprocess.PIPE)
    fd = process.stdout

    # Continue looking for all target outputs until all are found or 10 second timeout is reached
    lighter_found = reshape_found = False
    start_time = time.time()
    max_time = start_time + timeout
    found_targets = []
    full_lines = [] # Used for objective "cycles"
    content = []
    while time.time() < max_time and len(found_targets) < len(targets):
        newline = fd.readline().decode('utf-8')
        content.append(newline)
        for target in targets:
            if (target not in found_targets) and (target in newline) and ("ECHO" not in newline):
                found_targets.append(target)
                full_lines.append(newline)
                if debug: print("Found target line: " + newline)

    # Get the debug parent statements following the last matched target
    content.append(fd.readline().decode('utf-8'))
    content.append(fd.readline().decode('utf-8'))

    process.terminate()

    # Penalize cases where NARS fails to generate all target statements
    if len(found_targets) < len(targets):
        if debug: 
            print("NARS failed to generate all require target statements")
            print("Missing Targets:")
            for target in targets:
                if target not in found_targets:
                    print(target)
        return penalty_failed
    else:
        if optimization_objective == "chain_length":
            # Ignore all truth value updates (may drastically increase inference chain length despite being insignificant)
            found_targets = [target.split(" %")[0] for target in found_targets]
            # Average the length of longest chain from the ancestry tree of each statement
            return mean([longest_ancestry(target, 1, content) for target in found_targets])
        elif optimization_objective == "cycles":
            #Follow task not thoroughly tested
            return mean([int(re.findall('% {\d+', target)[0][3:]) for target in full_lines])
            
# In case a thread dies
def signal_handler(signum, frame):
    raise Exception("\tBatch timed out, retrying")

# Running multiple trials of objective function in parallel and taking average
def parallelize_objective(args):
    print("Iteration using params:\n" + str(args))
    losses = []
    for it in range(round(trials / cores)):
        success = False
        while not success:
            # Each batch is given a maximum time before it is assumed a worker hung
            signal.alarm(batch_TO)
            try:
                with mp.Pool(cores) as p:
                    batch = p.map(objective, [args] * cores)
                    print("\tBatch results: " + str(batch))
                losses += batch
                success = True
            # If not successful, print a message and try again
            except Exception as e:
                    print(str(e))

    loss = mean(losses)
    print("Hyperopt Iteration Loss: " + str(loss) + "\n")
    return loss

# =====================
# Execution begins here
# =====================

# In case subprocess pool hangs
signal.signal(signal.SIGALRM, signal_handler)

# Search space consisting of suggested top 4 parameters
space = {'DERIVATION_PRIORITY_LEAK': hp.uniform('DERIVATION_PRIORITY_LEAK', 0.1, 0.3),
        'VARIABLE_INTRODUCTION_COMBINATIONS_MAX': hp.quniform('VARIABLE_INTRODUCTION_COMBINATIONS_MAX', 0, 0, 1),
        'SEQUENCE_BAG_ATTEMPTS': hp.quniform('SEQUENCE_BAG_ATTEMPTS', 0, 0, 1),
        'TERM_LINK_MAX_MATCHED': hp.quniform('TERM_LINK_MAX_MATCHED', 30, 50, 1)}
print(space)
exit()
# Execute hyperopt param search
if debug:
    best = fmin(objective, space, algo=tpe.suggest, max_evals=num_evals)
else:
    best = fmin(parallelize_objective, space, algo=tpe.suggest, max_evals=num_evals)

print("Final Params:")
print(best)
