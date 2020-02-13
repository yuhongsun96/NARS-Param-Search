# Hyperparameter search for openNARS

What it does:
-------------
This is a hyperparameter tuning suite for the Non-Axiomatic Reasoning System for applied use cases. It uses Hyperopt to sample the user defined search space to find the best performing parameters given a set of Narsese input files. 
- For each set of parameters, it executes a user defined number of runs of NARS, each starting from a random initial state.
- NARS runs until all target statements in the Narsese file have been deduced by NARS or a specified timeout is reached.
- Each run of NARS is benchmarked with an objective functions. The final loss for a set of parameters is taken to be the average performance across the runs of NARS.
- A few predefined objective functions are available to choose from. Custom objectives can also be added in objectives.py.

How to Use:
-----------
1. The NARS jar is required to be in this directory. It can be built from the opennars git page:\
https://github.com/opennars/opennars

2. Recompile the java NARS wrapper with javac -cp .:* run_nars.java

3. Edit the parameters, input files and run configurations in config.json

4. Run with python3 param_search.py

