import subprocess
import re
import time
import multiprocessing as mp
from statistics import mean 
from hyperopt import hp, fmin, tpe, space_eval

# Turn on debug, only runs 1 hyperopt iteration with a single trial
debug = False
# Number of iterations of hyperopt
num_evals = 200
# Timeout limit in seconds for NARS to conclude all target statements
timeout = 10
# Failure penalty in case NARS fails to conclude all target statements
penalty_failed = 50
# Cores available for parallelizing
cores = 4
# Number of trials per hyperopt iteration (since NARS nondeterministic)
trials = 40 # Optimally should be multiple of cores


# Setup
targets = [ "(^lighter,{SELF},toothbrush)! %1.00;0.39%", \
            "(^reshape,{SELF},toothbrush)! %1.00;0.26%"]
if debug: num_evals = 1
debug_str_1 = "DEBUG: Parent Belief\t"
debug_str_2 = "DEBUG: Parent Task\t"
regex_null = re.compile(r'\s?null\s?')


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


# Objective: minimize the inference chain length taken for nars to conclude desired goals
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
    content = []
    while time.time() < max_time and len(found_targets) < len(targets):
        newline = fd.readline().decode('utf-8')
        content.append(newline)
        for target in targets:
            if (target not in found_targets) and (target in newline) and ("ECHO" not in newline):
                found_targets.append(target)
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
        # Ignore all truth value updates (may drastically increase inference chain length despite being insignificant)
        found_targets = [target.split(" %")[0] for target in found_targets]
        # Average the length of longest chain from the ancestry tree of each statement
        return mean([longest_ancestry(target, 1, content) for target in found_targets])

# Running multiple trials of objective function in parallel and taking average
def parallelize_objective(args):
    print("Iteration using params:\n" + str(args))
    losses = []
    for it in range(round(trials / cores)):
        with mp.Pool(cores) as p:
            batch = p.map(objective, [args] * cores)
            print("\tBatch results: " + str(batch))
        losses += batch
    loss = mean(losses)
    print("Hyperopt Iteration Loss: " + str(loss) + "\n")
    return loss


# Search space consisting of suggested top 4 parameters
space = {'DERIVATION_PRIORITY_LEAK': hp.uniform('DERIVATION_PRIORITY_LEAK', 0.1, 0.9), 
        'VARIABLE_INTRODUCTION_COMBINATIONS_MAX': hp.quniform('VARIABLE_INTRODUCTION_COMBINATIONS_MAX', 0, 20, 1),
        'SEQUENCE_BAG_ATTEMPTS': hp.quniform('SEQUENCE_BAG_ATTEMPTS', 0, 50, 1),
        'TERM_LINK_MAX_MATCHED': hp.quniform('TERM_LINK_MAX_MATCHED', 0, 50, 1)}

# Execute hyperopt param search
if debug:
    best = fmin(objective, space, algo=tpe.suggest, max_evals=num_evals)
else:
    best = fmin(parallelize_objective, space, algo=tpe.suggest, max_evals=num_evals)

print("Final Params:")
print(best)
