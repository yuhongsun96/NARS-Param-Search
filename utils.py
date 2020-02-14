""" Utility functions for objectives

This file contains utility functions to reduce clutter in objectives.py
For helping organization if user wishes to add custom objectives

"""

import re

regex_null = re.compile(r'\s?null\s?')
debug_str_1 = "DEBUG: Parent Belief\t"
debug_str_2 = "DEBUG: Parent Task\t"
def longest_ancestry(statement, text, depth, debug, failure_penalty):
    """ Recursive tree traversal through parents of statement

    Args:
        statement: pattern to search for in the text
        text: body of text to search pattern in, 
              only contains NARS output which came earlier than statement
        depth: Current depth from the top (original target statement from Narsese file)
        debug: Very verbose output showing every statement of interest and it's parents
        
    """
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
        return failure_penalty

    if debug: print("parent 1: " + parent1)
    if debug and regex_null.search(parent1): print("Terminal case parent 1")
    if debug: print("parent 2: " + parent2)
    if debug and regex_null.search(parent2): print("Terminal case parent 2")

    # Failsafe, the two lines following the OUT: line with target should be the 2 Debug parent statements
    if debug_str_1 not in parent1 or debug_str_2 not in parent2:
        print("Statement found in:\n" + text[last_line])
        print("Parent 1:\n" + parent1)
        print("Parent 2:\n" + parent2)
        print("Unexpected parent string")
        return failure_penalty

    # Trim off label and truth value
    parent1 = parent1.split(debug_str_1)[1].split(" %")[0]
    parent2 = parent2.split(debug_str_2)[1].split(" %")[0]

    # If parent is null, that branch is done, else call longest ancestry again
    len1 = depth + 1 if regex_null.search(parent1) else longest_ancestry(parent1, text[:ind], depth + 1, debug)
    len2 = depth + 1 if regex_null.search(parent2) else longest_ancestry(parent2, text[:ind], depth + 1, debug)

    # Return longest path of ancestry tree
    return max(len1, len2)
