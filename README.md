# Hyperparameter search for openNARS

What it does:
-------------
Provide a hyperparameter tuning suite for the Non-Axiomatic Reasoning System for applied use cases. Uses Hyperopt to sample a user defined search space to find the best performing parameters given a set of Narsese input files. 

How to Use:
-----------
1. The NARS jar is required to be in this directory. It can be built from the opennars git page:\
https://github.com/opennars/opennars

2. Recompile the java NARS wrapper with javac -cp .:* run_nars.java

3. If desired, edit the parameters, input files and run configurations in config.json.

4. If desired, a custom objective function can be added in objectives.py and pointed to by "optimization objective" in config.json.

4. Run with python3 param_search.py

Configuring Runs:
-----------------
Configurations are done through config.json
- NARS input files: A list of Narsese files to pass to NARS to reason about
- NARS parameters: System parameters for NARS. Must take format of either \["name", min-val, max-val\] or \["name", "True/False"\]. Refer to defaultConfig.xml for availble NARS parameter fields.
- optimization objective: Benchmarking criteria for a NARS run. Must be the name of one of the functions in objectives.py. Default available functions include: "chain_length" (to minimize the length of the longest inference chain to reach a target statement), "num_cycles" (to minimize number of NARS cycles before deducing target statement), and "real_time" (to minimize the time NARS takes to conclude the target statement).
- failure penalty: The penalty value for runs where NARS fails to deduce all target statements.
- Hyperopt iterations: Number of Hyperopt iterations to run (number of sets of parameters to test)
- NARS runs per iteration: Number of trials of NARS to run and average for a single iteration of Hyperopt (1 set of parameters).
- cpu threads: Number of cpu threads available for parallelizing runs of NARS.
- NARS timeout: Time in seconds before it is assumed NARS will not be able to deduce the target statements.
- require exact truth value: Whether a derived NARS statement can match a target even if the truth values are not an exact match.
- batch timeout: Time in seconds before it is assumed one of the subprocesses hung and a batch needs to be run again.
- debug: Very verbose run of only a single iteration of hyperopt and a single run of NARS. "True" to turn on.

Execution Details:
------------------
- A set of parameters to benchmark is provided by the Hyperopt framework.
- For each set of parameters, executes a user defined number of runs of NARS, each starting from a random initial state.
- NARS runs until all target statements in the Narsese file have been deduced by NARS or a specified timeout is reached.
- Each run of NARS is benchmarked with an objective functions. The final loss for a set of parameters is taken to be the average performance across the runs of NARS.
- The set of parameters that led to the optimal result is kept.

