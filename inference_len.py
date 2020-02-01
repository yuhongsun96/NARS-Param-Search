import subprocess
import re
import time
from statistics import mean 
from hyperopt import hp, fmin, tpe, space_eval

# Turn on debug, only runs 1 hyperopt iteration
debug = False
# Number of iterations of hyperopt
num_evals = 1
# Timeout limit in seconds for NARS to conclude all target statements
timeout = 10
# Failure penalty in case NARS fails to conclude all target statements
penalty_failed = 100

targets = [ "(^lighter,{SELF},toothbrush)! %1.00;0.39%", \
            "(^reshape,{SELF},toothbrush)! %1.00;0.26%"]

if debug: num_evals = 1

def longest_ancestry(statement, depth, text):
    print(statement)
    return 1

# Objective: minimize the inference chain length taken for nars to conclude desired goals
def objective(args):
    # Specify NARS Parameters
    process_cmd = ['java', '-cp', '.:opennars-3.0.4-SNAPSHOT.jar', 'run_nars', \
        str(args['DERIVATION_PRIORITY_LEAK']), \
        str(int(args['VARIABLE_INTRODUCTION_COMBINATIONS_MAX'])), \
        str(int(args['SEQUENCE_BAG_ATTEMPTS'])), \
        str(int(args['TERM_LINK_MAX_MATCHED']))]
    
    # Execute NARS in shell mode and capture output
    process = subprocess.Popen(process_cmd, stdout=subprocess.PIPE)
    fd = process.stdout
    
    # Continue looking for all target outputs until all are found or 10 second timeout is reached
    lighter_found = reshape_found = False
    start_time = time.time()
    max_time = start_time + timeout
    found_targets = []
    content = ""
    while time.time() < max_time and len(found_targets) < len(targets):
        newline = fd.readline().decode('utf-8')
        content += newline
        for target in targets:
            if (target not in found_targets) and (target in newline) and ("ECHO" not in newline):
                found_targets.append(target)
    
    process.terminate()

    # Heavily penalize cases where NARS fails to generate all target statements
    if len(found_targets) < len(targets):
        return penalty_failed
    else:
        # Ignore all truth value updates
        found_targets = [target.split(" %")[0] for target in found_targets]
        # Average the length of longest chain from the ancestry tree of each statement
        return mean([longest_ancestry(target, 1, content) for target in found_targets])

# Search space consisting of suggested top 4 parameters
space = {'DERIVATION_PRIORITY_LEAK': hp.uniform('DERIVATION_PRIORITY_LEAK', 0, 1), 
        'VARIABLE_INTRODUCTION_COMBINATIONS_MAX': hp.quniform('VARIABLE_INTRODUCTION_COMBINATIONS_MAX', 0, 100, 1),
        'SEQUENCE_BAG_ATTEMPTS': hp.quniform('SEQUENCE_BAG_ATTEMPTS', 0, 100, 1),
        'TERM_LINK_MAX_MATCHED': hp.quniform('TERM_LINK_MAX_MATCHED', 0, 100, 1)}

best = fmin(objective, space, algo=tpe.suggest, max_evals=num_evals)

print(best)
