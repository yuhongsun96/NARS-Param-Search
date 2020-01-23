import subprocess
#subprocess.call(['java', '-cp', '.:opennars-gui-3.0.3-SNAPSHOT.jar', 'run_nars']) 

# define an objective function
def objective(args):
    process_cmd = ['java', '-cp', '.:opennars-3.0.4-SNAPSHOT.jar', 'run_nars', \
        str(args['DERIVATION_PRIORITY_LEAK']), \
        str(int(args['VARIABLE_INTRODUCTION_COMBINATIONS_MAX'])), \
        str(int(args['SEQUENCE_BAG_ATTEMPTS'])), \
        str(int(args['TERM_LINK_MAX_MATCHED']))]
    #print(process_cmd)
    process = subprocess.call(process_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stderr = process.communicate()[1]
    stdout = process.communicate()[0]
    while True:
        print("reached")
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    print("FINISHED")
    return 1

# define a search space
from hyperopt import hp
space = {'DERIVATION_PRIORITY_LEAK': hp.uniform('DERIVATION_PRIORITY_LEAK', 0, 1), 
        'VARIABLE_INTRODUCTION_COMBINATIONS_MAX': hp.quniform('VARIABLE_INTRODUCTION_COMBINATIONS_MAX', 0, 100, 1),
        'SEQUENCE_BAG_ATTEMPTS': hp.quniform('SEQUENCE_BAG_ATTEMPTS', 0, 100, 1),
        'TERM_LINK_MAX_MATCHED': hp.quniform('TERM_LINK_MAX_MATCHED', 0, 100, 1)}

# minimize the objective over the space
from hyperopt import fmin, tpe, space_eval
best = fmin(objective, space, algo=tpe.suggest, max_evals=100)

print(best)
# -> {'a': 1, 'c2': 0.01420615366247227}
#print(space_eval(space, best))
# -> ('case 2', 0.01420615366247227}


