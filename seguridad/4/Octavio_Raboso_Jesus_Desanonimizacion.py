#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 11:13:57 2022

@author: jesus
"""

### LOAD LIBRARIES ###
import pandas as pd
import numpy as np
import itertools
import string
import hashlib


### DEFINE FNUCTION ###
def deanonymize_taxi(file):
    """
    Deanonymize taxi NYC dataset (or others). The input dataset must contain (at least)
    a colum named 'medallion' and a column names 'hack_license'. Both columns must have been
    anonymized with MD5 (hash function with a 128-bit hash value). All the possible values 
    used to generate the MD5 code must be known. Write deanonymized .cvs.
    
    
    I guess this code will not work on PCs dut to problems with RAM memory. The 
    process will be killed by the OOM killer (Out Of Memory Killer). But this would be 
    a good signal: without it, your machine would simply become unresponsive. But I had no 
    problems coding on datasciencehub.ifca.es (sorry for the bad use of our cloud, i've 
    already removed trip_data.csv and the deanonymized datsaet)
    
    Alternatives:
     - Improve python code so it uses less memory
     - Get more RAM, but seems like a band-aid.
     - Write dicts on files (.hdf5 ?, cvs?) and read line by line. Disadvantage: requires 
       much more time.
    
    Parameters
    ----------
    file : str
        File name or path. Must be .csv or similar. 
    
    Return
    ------
    None
    """

    # Read a comma-separated values (csv) into DataFrame. In our case: reading the input file.
    data = pd.read_csv(file)
    
    # Select columns "medallion" and "hacklicense".
    # np.unique to find the unique elements of an array. 
    # Do not need to deanonymaze the same MD5 more than once.
    medallions_md5 = np.unique(data["medallion"])
    licenses_md5 = np.unique(data["hack_license"])


    ### DEANONYMIZE HACK LICENSES (FOR NYC) ### 
    
    ## GENERATE ALL POSSIBLE VALUES FOR HACK LICENSES ##
    
    # HACK LICENSES WITH 6 DIGITS AND 0 PADDED
    # itertools.product: cartesian product, equivalent to a nested for-loop
    #    For example, itertools.product(A, B) returns the same as  ((x,y) for x in A for y in B)
    #    To compute the product of an iterable with itself, the number of repetitions are
    #       specified in the *repeat* keyword argument
    # string.digits: the string '0123456789'.
    # .join(i): join items into one string. List comprehension is used. 
    licenses_6digits_padded = [''.join(i) for i in itertools.product(string.digits, repeat = 6)]
        
    # For the licenses previously generated, compute MD5 value and save in a dict whose keys
    # are the MD5s and whose values are the license uses to generate the MD5
    licenses_dict = {hashlib.md5(x.encode()).hexdigest().upper() : x for x in licenses_6digits_padded}
    
    # HACK LICENSES WITH 5 DIGITS, NOT 0 PADDED.
    # Same idea as before. Use range() to return a sequence of numbers from o to 100000.
    licenses_6digits_no_padded  = [str(i) for i in range(100000)]
    
    # Update dictionary
    licenses_dict.update({hashlib.md5(x.encode()).hexdigest().upper() : x for x in licenses_6digits_no_padded})
    
    # Remove variable. Not gonna be used anymore. ¿Troubles with RAM memory?
    del licenses_6digits_no_padded
    
    # HACK LICENSES WITH 7 DIGITS
    # We already generated all possible numbers with 6 digits and 0 padded. We just need to add "5" at the
    # beggining of them. We create a lambda function to add that 5 at the beggining.
    # We use map to apply the lambda function to each 6 digit-0 padded number.
    # Convert map object to list for future work. 
    licenses_7digits = list(map(lambda x: "5" + x, licenses_6digits_padded))
    # Update dictionary
    licenses_dict.update({hashlib.md5(x.encode()).hexdigest().upper() : x for x in licenses_7digits})
    
    # Remove variables. Not gonna be used anymore. ¿Troubles with RAM memory?
    del licenses_7digits, licenses_6digits_padded

    # DEANONYMIZE
    # Empty list to store MD5s unable to deanonymize
    licenses_not_found = []
    # Consides each hack_license from the input dataset
    for elem in licenses_md5:
        # If unable to deanonymize: 
        if elem not in licenses_dict.keys():
            # Add to not fonud list
            licenses_not_found.append(elem)
            # Replace all its occurrences with NOT FOUND ¿other special value?
            data["hack_license"].replace({elem : "NOT FOUND"}, inplace = True)
        # If able to deanonymize
        else:
            # Replace properly
            data["hack_license"].replace({elem : str(licenses_dict[elem])}, inplace = True)

    # Remove variable. Not gonna be used anymore. ¿Troubles with RAM memory?
    del licenses_dict
        
    # Display MD5s unable to deanonymize  
    print("Unable to deanonymize %s hack licenses !" % len(licenses_not_found))
    for elem in licenses_not_found:
        print("   License with md5 %s not found" % elem)



    ### DEANONYMIZE MEDALLIONS (FOR NYC) ### 
    
    ## GENERATE ALL POSSIBLE VALUES FOR MEDALLIONS ##
    
    # NUMBER + LETTER + NUMBER + NUMBER (e.g. 5X55)
    # Same idea as before.
    # itertools.product: cartesian product, equivalent to a nested for-loop
    # string.digits: the string '0123456789'.
    # .join(i): join items into one string. List comprehension is used. 
    
    # number + number
    nx2 = [''.join(i) for i in itertools.product(string.digits, repeat = 2)]
    
    # string.ascii_letters: The concatenation of the
    # ascii_lowercase 'abcdefghijklmnopqrstuvwxyz'
    # and ascii_uppercase constants 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.
    # letter + number + number
    temp = [''.join(i) for i in itertools.product(string.ascii_letters, nx2)]
    
    # Generate all possible combitations of number + letter + number + number
    nx1_lx1_nx2 = [''.join(i) for i in itertools.product(string.digits, temp)]
    
    # Create dictionary as before
    medallions_dict = {hashlib.md5(x.encode()).hexdigest().upper() : x for x in nx1_lx1_nx2}
    
    # Remove variables. Not gonna be used anymore. ¿Troubles with RAM memory?
    del temp, nx1_lx1_nx2
    
    # LETTER + LETTER + NUMBER + NUMBER + NUMBER
    # number + number + number
    nx3 = [''.join(i) for i in itertools.product(string.digits, nx2)]
    
    # Remove variables. Not gonna be used anymore. ¿Troubles with RAM memory?
    del nx2
    
    # letter + letter
    lx2 = [''.join(i) for i in itertools.product(string.ascii_letters, repeat = 2)]
    
    # letter + letter + number + number + number
    lx2_nx3 = [''.join(i) for i in itertools.product(lx2, nx3)]
    
    # Update dictionary
    medallions_dict.update({hashlib.md5(x.encode()).hexdigest().upper() : x for x in lx2_nx3})
    
    # Remove variables. Not gonna be used anymore. ¿Troubles with RAM memory?
    del lx2_nx3

    
    # Denaonymize. Same idea as before.
    # I know not all possible values have been generated but it's a huge dictionary
    # so it could give RAM memory problems
    for elem in medallions_md5:
        if elem in medallions_dict.keys():
            data["medallion"].replace({elem : str(medallions_dict[elem])}, inplace = True)
            medallions_md5 = np.setdiff1d(medallions_md5, elem)
    
    # WHY REPLACING WITH str(medallions_dict[elem]) and not medallions_dict[elem]?
    # Medallions like 7E92 or 6E16 could be interpreted as scientific notation and not string when 
    # reading the deanonymized csv
    
    # Remove variables. Not gonna be used anymore. ¿Troubles with RAM memory?
    del medallions_dict
    
    # LETTER + LETTER+ LETTER + NUMBER + NUMBER + NUMBER
    # letter + letter + letter
    lx3 = [''.join(i) for i in itertools.product(string.ascii_letters, lx2)]
    
    # Remove variables. Not gonna be used anymore. ¿Troubles with RAM memory?
    del lx2
    
    # letter + letter + letter + number + number + number + number
    lx3_nx3 = [''.join(i) for i in itertools.product(lx3, nx3)]
    
    # Update dictionary
    medallions_dict = {hashlib.md5(x.encode()).hexdigest().upper() : x for x in lx3_nx3}
    
    # Remove variables. Not gonna be used anymore. ¿Troubles with RAM memory?
    del lx3_nx3, nx3, lx3
    
    # Deanonymize. Same idea as for hack licenses
    medallions_not_found = []
    for elem in medallions_md5:
        if elem not in medallions_dict.keys():
            medallions_not_found.append(elem)
            data["medallion"].replace({elem : "NOT FOUND"}, inplace = True)
        else:
            data["medallion"].replace({elem : str(medallions_dict[elem])}, inplace = True)
    
    print("Unable to deanonymize %s medallions !" % len(medallions_not_found))
    for elem in medallions_not_found:
        print("   Medallion with md5 %s not found" % elem)
    
    
    # Wride deanonymizev .csv
    data.to_csv("taxi_NYC_deanonymized.csv")
    
if __name__ == "__main__":
    file = 'trip_data.csv'
    deanonymize_taxi(file)
    

    