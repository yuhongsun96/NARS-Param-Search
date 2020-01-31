import subprocess
import re
import time
from hyperopt import hp, fmin, tpe, space_eval

#NOTE: to understand the workings better, uncomment out any of the lines ending with DEBUG and change num_evals to 1
num_evals = 1

# Objective: minimize iterations taken for nars to conclude desired goals
def objective(args):
    # Run NARS with specified parameters
    process_cmd = ['java', '-cp', '.:opennars-3.0.4-SNAPSHOT.jar', 'run_nars', \
        str(args['DERIVATION_PRIORITY_LEAK']), \
        str(int(args['VARIABLE_INTRODUCTION_COMBINATIONS_MAX'])), \
        str(int(args['SEQUENCE_BAG_ATTEMPTS'])), \
        str(int(args['TERM_LINK_MAX_MATCHED']))]
    #print("Running: " + str(process_cmd) + "\n") #DEBUG
    process = subprocess.Popen(process_cmd, stdout=subprocess.PIPE)
    fd = process.stdout
    
    # Continue until both goals are seen or 10 second timeout is reached
    lighter_found = reshape_found = False
    start_time = time.time()
    max_time = start_time + 10
    while time.time() < max_time and (not lighter_found or not reshape_found):
        newline = fd.readline().decode('utf-8')
        print(newline)
        if "ECHO" not in newline and "(^lighter,{SELF},toothbrush)! %1.00;0.39%" in newline and not lighter_found:
            #print(newline) #DEBUG
            lighter_iter = int(re.findall('% {\d+', newline)[0][3:])
            lighter_found = True
        if "ECHO" not in newline and "(^reshape,{SELF},toothbrush)! %1.00;0.26%" in newline and not reshape_found:
            #print(newline) #DEBUG
            reshape_iter = int(re.findall('% {\d+', newline)[0][3:])
            reshape_found = True
    
    # Return sum of iterations at which goals were seen or 100000 for failed run
    process.terminate()
    if not lighter_found or not reshape_found:
        return 100000
    #print("Loss for 1 trial with these params: " + str(lighter_iter + reshape_iter) + "\n") #DEBUG
    return lighter_iter + reshape_iter

# Search space consisting of suggested top 4 parameters
space = {'DERIVATION_PRIORITY_LEAK': hp.uniform('DERIVATION_PRIORITY_LEAK', 0, 1), 
        'VARIABLE_INTRODUCTION_COMBINATIONS_MAX': hp.quniform('VARIABLE_INTRODUCTION_COMBINATIONS_MAX', 0, 100, 1),
        'SEQUENCE_BAG_ATTEMPTS': hp.quniform('SEQUENCE_BAG_ATTEMPTS', 0, 100, 1),
        'TERM_LINK_MAX_MATCHED': hp.quniform('TERM_LINK_MAX_MATCHED', 0, 100, 1)}

best = fmin(objective, space, algo=tpe.suggest, max_evals=num_evals)

print(best)
