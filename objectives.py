""" Objective functions to provide a single value loss for hyperopt

This module defines the objective functions that are available in config.json
To add objectives, simply add another method, no further mentions of it are needed elsewhere
All methods must take the same parameters and return a single int/float/double

    Args:
        target: target statement string defined in the Narsese file,
                truth values included depending on "require exact truth value" in config.json
        content: NARS output over the lifetime of the run
        nars_run_time: total time taken over the lifetime of the NARS run
                       the time includes the random-state start delay
        debug: optionally the objective functions can print extra information if debug is on
        failure_penalty: Penalty for a failure case, set in config.json

"""

__authors__ = "Yuhong Sun"
__license__ = "MIT License"

import re
import utils

# The longest path through the derivation ancestry tree of the target statement
def chain_length(target, content, nars_run_time, debug, failure_penalty):
    return utils.longest_ancestry(target, content, 1, debug, failure_penalty)

# The number of NARS cycles to reach the target statement
def num_cycles(target, content, nars_run_time, debug, failure_penalty):
    for line in content:
        if (target in line) and ("ECHO:" not in line) and ("IN:" not in line):
            return int(re.findall(r'% {\d+', line)[0][3:])
    # Failsafe, should not happen
    print("Failed to find target in content")
    return failure_penalty

# The time in seconds for the complete run of NARS until all target statemnts were derived
def real_time(target, content, nars_run_time, debug, failure_penalty):
    return round(nars_run_time, 2)


