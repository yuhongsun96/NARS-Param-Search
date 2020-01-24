# Hyperparameter search for openNARS using toothbrush.nal

To run, first compile and replace opennars-3.0.4-SNAPSHOT.jar from the opennars\
Recompile with javac -cp \\* *.java

Run with python3 param_search.py

**Brief Overview:**\
run_nars.java is a wrapper to invoke NARS in the shell with all default parameters excepting the 4 passed in through args
It takes in the toothbrush.nal file

param_search.py uses hyperopt with the search space defined by the 4 parameters:\
DERIVATION_PRIORITY_LEAK, VARIABLE_INTRODUCTION_COMBINATIONS_MAX, SEQUENCE_BAG_ATTEMPTS and TERM_LINK_MAX_MATCHED
It invokes run_nars and pipes the output for analysis to look for the relevent goals from NARS output
The loss for hyperopt optimization is the sum of the cycles where the goals first appear
Using hyperopt, the end result is the best loss and the hyperparam values that resulted in it.
