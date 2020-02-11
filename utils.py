import json

# Run initial setup when this file is imported
with open('config.json', 'r') as config_json:
    config = json.load(config_json)

inputs = config['NARS input files']
params = config['NARS parameters']
debug = config['debug']
objective = config['optimization objective']
failure_penalty = config['failure penalty']
hyperopt_iters = config['hyperopt iterations']
runs_per_iter = config['NARS runs per iteration']
cores = config['cpu cores']
NARS_TO = config['NARS timeout']
batch_TO = config['batch timeout']
exact_TV = config['require exact truth value']

if failure_penalty < 10000 and objective == "cycles":
    print("Consider using a higher failure penalty (at least 10000) for optimization objective = cycles")
    time.sleep(2)

# Extract the target statements given an input Narsese file
def extract_targets(nars_file):
    print("Processing NARS input file: " + nars_file + "\n")
    targets = []
    # Target statements expected to begin with the following pattern in the Narsese file.
    target_stamp = "\'\'outputMustContain(\'"
    with open(nars_file, "r") as narsese:
        for line in narsese:
            if target_stamp in line:
                if exact_TV: targets.append(line.split(target_stamp)[1][:-3])
                else: targets.append(line.split(target_stamp)[1].split("%")[0])
    if debug:       
        print("Found Target Statements: ")
        [print("\t" + target) for target in targets]
        print("\n")
        time.sleep(1)
    return targets

# In case a thread dies
def signal_handler(signum, frame):
    raise Exception("\tBatch timed out, retrying")

# Get the longest path through ancestry tree of statement
def longest_ancestry(statement, depth, text):
    return 1

def obj_chain_length:
    return 1

def obj_cycle_count:
    return 1



