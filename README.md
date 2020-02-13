# Hyperparameter search for openNARS

What it does:
-------------
Provide a hyperparameter tuning suite for the Non-Axiomatic Reasoning System for applied use cases. Uses Hyperopt to sample a user defined search space to find the best performing parameters given a set of Narsese input files. 

How to Use:
-----------
1. The NARS jar is required to be in this directory. It can be built from the opennars git page:\
https://github.com/opennars/opennars

2. Recompile the java NARS wrapper with javac -cp .:* run_nars.java

3. Edit the parameters, input files and run configurations in config.json

4. Run with python3 param_search.py

Configuring Runs:
-----------------
Configurations are done through config.json
- NARS input files: A list of Narsese files to pass to NARS to reason about
- NARS parameters: System parameters for NARS. \Should take format of either \["name", min-val, max-val\] or \["name", "True/False"\]. Refer to defaultConfig.xml for availble NARS parameter fields.
- optimization objective: Benchmarking criteria for a NARS run. \Must be the name of one of the functions in objectives.py. Default available functions include: \t"chain_length" (to minimize the length of the longest inference chain for a target statement), "num_cycles" (to minimize number of NARS cycles before deducing target statement), and "real_time" (to minimize the time taken before NARS is able to conclude the target statement).
- debug: Very verbose run of only a single iteration of hyperopt and a single run of NARS. "True" to turn on.


- For each set of parameters, it executes a user defined number of runs of NARS, each starting from a random initial state.
- NARS runs until all target statements in the Narsese file have been deduced by NARS or a specified timeout is reached.
- Each run of NARS is benchmarked with an objective functions. The final loss for a set of parameters is taken to be the average performance across the runs of NARS.
- A few predefined objective functions are available to choose from. Custom objectives can also be added in objectives.py.
