# Warning: The execution of this file will automatically remove *.log, ctest-*.json,
#          and all auto-generated [input_yaml]_[#iter_id].yaml files from this directory.
#          Would potentially overwrite the original yaml file if the execution fails.

# From Albany/tools - yaml read/write

# Need: pip install --user pandas
# Need: pip install --user ruamel.yaml
# Need: pip install --user scikit-learn

# Import libraries
import argparse
import getopt
import glob
import json
import numpy as np
import os
import pandas as pd
import random
import statistics
import subprocess
import sys
from collections import Counter
from math import exp, log
from scipy.stats import expon, truncnorm, truncexpon
from sklearn.model_selection import ParameterGrid, ParameterSampler
from ruamel.yaml import YAML

yaml = YAML(typ='rt')  # Round trip loading and dumping
yaml.preserve_quotes = True
yaml.width = 1000

def read_yaml(filename):
    '''
    Parse the input yaml file and generate a dictionary object.
    Parameters: 
        filename(string): input yaml filename
    Returns:
        dictionary(dictionary): dictionary from yaml
    '''
    with open(filename) as file:
        dictionary = yaml.load(file)
    return dictionary

def write_yaml(dictionary, filename):
    '''
    Accept a dictionary and produce a YAML document.
    Parameters:
        dictionary(dictionary): object to be dumped
        filename(string): output yaml filename
    '''
    with open(filename, 'w') as file:
        yaml.dump(dictionary, file)
        file.write('...\n')

###############################################################################
def run_bash(command):
    '''
    Run a bash command.
    '''
    return subprocess.run(command, shell=True, executable='/bin/bash')

def run_sim(iter, inFile):
    '''
    Run yaml input file.
    Parameters:
        iter(integer): represents iteration
        inFile(file): the input yaml file
    '''
    # Check if mesh-pop exists
    if os.path.isdir('mesh-pop-wdg'):
      print('Populated mesh already exists!')
    else:
      run_bash('ctest -L "pop"')

    # Run simulation
    run_bash('ctest -L "tune-gpu" --timeout 90')

    # Generate input file
    newInFile = inFile.split('.')[0] + '_' + str(iter) + '.' + inFile.split('.')[1]
    run_bash('cp ' + inFile + ' ' + newInFile)

    # Generate output file
    run_bash('cp Testing/Temporary/LastTest.log LastTest_'+str(iter)+'-0.log')


###############################################################################
def get_truncated_normal(mean=1, sd=0.1, low=0.8, upp=1.2):
    '''
    Generate a truncated normal continuous distribution with range.
    '''
    return truncnorm(a=(low-mean)/sd, b=(upp-mean)/sd, loc=mean, scale=sd)

def get_truncated_expon(low=0.7, upp=1.4, sd=0.3):
    '''
    Generate a truncated exponential continuous distribution with range.
    '''
    return truncexpon(b=(upp-low)/sd, loc=low, scale=sd)

def random_search_multi(inFile, n_iter, seed):
    '''
    Run experiment with Random Search.
    Parameters:
        inFile(file): the input yaml file
        n_iter(integer): a nonneg integer that represents the current round of iteration
        seed(integer): an integer between 0 and 2**32 - 1 inclusive
    Returns:
        iter_param_dict(dictionary): {#iter:{parameter_to_change:new_value}} where
                                    #iter is the unique iter id for each experiment
    '''
    # Read input file
    inputDict = read_yaml(inFile)

    # Extract MueLu dictionary
    linsolDict = inputDict['ANONYMOUS']['Piro']['NOX']['Direction']['Newton']['Stratimikos Linear Solver']
    muDict = linsolDict['Stratimikos']['Preconditioner Types']['MueLu']

    # Parameter to change
    paramList_1 = muDict['Factories']['mySmoother1']['ParameterList']
    paramList_4 = muDict['Factories']['mySmoother4']['ParameterList']

    # Define Random State with the Mersenne Twister pseudo-random number generator
    random_state = np.random.RandomState(seed)

    TYPE = ['Two-stage Gauss-Seidel', 'MT Gauss-Seidel']
    DAMPING_FACTOR_1 = get_truncated_normal(0.4, 0.2, 0.1, 0.7)
    SWEEP_1 = list(range(1, 3))
    SWEEP_4 = list(range(1, 5))

    param_grid_1 = {'relaxation: type': TYPE,
                    'relaxation: sweeps': SWEEP_1,
                    'relaxation: inner damping factor': DAMPING_FACTOR_1
                   }
    param_grid_4 = {'relaxation: type': TYPE,
                    'relaxation: sweeps': SWEEP_4
                   }
    grid_1 = ParameterSampler(param_grid_1, n_iter=n_iter, random_state=random_state)
    grid_4 = ParameterGrid(param_grid_4)
    
    param_1 = [dict((k, v) for (k, v) in d.items()) for d in grid_1]
    param_4 = [dict((k, v) for (k, v) in d.items()) for d in grid_4]

    param_1 = [{ k: float(round(v,4)) if isinstance(v,float) else v for k,v in x.items()} for x in param_1]
    #param_4 = [{ k: float(round(v,4)) if isinstance(v,float) else v for k,v in x.items()} for x in param_4]

    random_mS4 = random.choices(list(range(0, len(param_4))), k = n_iter)

    #grid = ParameterGrid(param_grid)
    #print("TOTAL NUM OF CASES TO BE RUN: {}".format(len(list(grid))))
    
    # Run simulations
    #ite = 0 # current #iter id
    iter_param_dict_1 = dict()
    iter_param_dict_4 = dict()
    
    for i in range(len(param_1)):
        print('\n')
        print("########################## CASE {} ##########################".format(i))
        paramList_1.update(param_1[i])
        print("[mySmoother1] ", param_1[i])
        paramList_4.update(param_4[random_mS4[i]])
        print("[mySmoother4] ", param_4[random_mS4[i]])

        write_yaml(inputDict, inFile)
        run_sim(i, inFile)
        
        iter_param_dict_1.update({str(i):param_1[i]})
        iter_param_dict_4.update({str(i):param_4[random_mS4[i]]})
        
    print('\n')
    print('################### TOTAL NUM OF CASES: {} ##################'.format(len(param_1)))
    run_bash('python ctest2json.py')
    return iter_param_dict_1, iter_param_dict_4

def random_search_single(inFile, n_iter, seed):
    '''
    Run experiment with Random Search.
    Parameters:
        inFile(file): the input yaml file
        n_iter(integer): a nonneg integer that represents the current round of iteration
        seed(integer): an integer between 0 and 2**32 - 1 inclusive
    Returns:
        iter_param_dict(dictionary): {#iter:{parameter_to_change:new_value}} where
                                    #iter is the unique iter id for each experiment
    '''
    # Read input file
    inputDict = read_yaml(inFile)

    # Extract MueLu dictionary
    linsolDict = inputDict['ANONYMOUS']['Piro']['NOX']['Direction']['Newton']['Stratimikos Linear Solver']
    muDict = linsolDict['Stratimikos']['Preconditioner Types']['MueLu']

    # Parameter to change
    paramList = muDict['Factories']['mySmoother1']['ParameterList']

    # Define Random State with the Mersenne Twister pseudo-random number generator
    random_state = np.random.RandomState(seed)

    DAMPING_FACTOR = get_truncated_normal()
    #DAMPING_FACTOR = get_truncated_expon()
    SWEEPS = list(range(1, 2))

    param_distributions = {'relaxation: damping factor': DAMPING_FACTOR,
                           'relaxation: sweeps': SWEEPS}

    sampler = ParameterSampler(param_distributions,
                               n_iter=n_iter,
                               random_state=random_state)
    # Run simulations
    ite = 0 # current #iter id
    iter_param_dict = dict()
    for params in sampler:
        print('\n')
        print("########################## CASE {} ##########################".format(ite))
        # Change parameter
        for key, value in params.items():
            if key in paramList:
                # round float to 4 digits
                if not isinstance(value, int): value = (float)(round(value, 4))
                print('{0}: {1}'.format(key, value))
                paramList[key] = value
        iter_param_dict.update({str(ite):params})
        # Write input file
        write_yaml(inputDict, inFile)
        # Run yaml input file
        run_sim(ite, inFile)
        ite = ite + 1
    print('\n')
    print('################### TOTAL NUM OF CASES: {} ##################'.format(ite))
    run_bash('python ctest2json.py')
    return iter_param_dict

def get_time_randomsearch(filenames, case):
    '''
    Return a dictionary with time extracted from the output json files.
    Parameters:
        filenames(list): a list that contains ctest-*.json in this directory
        case(string): a string that represents the targeted casename from output
    Returns:
        iter_time_dict(dictionary): {#iter:Albany_Total_Time} where
                                    #iter is the unique iter id for each experiment
    '''
    iter_time_dict = dict()
    iter_totaltime_dict = dict()
    iter_bool_dict = dict()
    for each_file in filenames:
        with open(each_file) as f:
            dat = json.load(f)
            # ensure the test passed to get timer -- otherwise set to arbitrary large
            if dat.get(case, {}).get('passed') is True:
                time_linearsolve = dat.get(case, {}).get('timers', {}).get('NOX Total Linear Solve:')
                time_precondition = dat.get(case, {}).get('timers', {}).get('NOX Total Preconditioner Construction:')
                time = float(time_linearsolve) + float(time_precondition)
                totaltime = dat.get(case, {}).get('timers', {}).get('Albany Total Time:')
                bool_passed = True
            else:
                time = float('inf')
                totaltime = dat.get(case, {}).get('timers', {}).get('Albany Total Time:')
                bool_passed = False
            # extract time value and add to dictionary
            # output_num is the current #iter id 
            output_num = each_file.split('-')[-1]
            output_num = os.path.splitext(output_num)[0]
            iter_time_dict.update({output_num:time})
            iter_totaltime_dict.update({output_num:totaltime})     
            iter_bool_dict.update({output_num:bool_passed})   
    return iter_time_dict, iter_totaltime_dict, iter_bool_dict

###############################################################################
def get_casename(yamlfile):
    '''
    Get the corresponding casename from cmake file to minimize hardcoding.
    Parameters: 
        yamlfile(string): input yaml filename
    Returns:
        extract(string): corresponding casename
    '''
    target = ''
    with open('CTestTestfile.cmake', 'r') as f:
        for line in f:
            if (line.startswith("add_test")) and (yamlfile in line):
                target = next(f)
                break
        extract = target.split(' ')[0]
        extract = extract[21:]
    print("CASENAME:", extract)
    return extract

def revise_keystring(count, dic):
    return { str(count)+'::'+str(key) : (revise_keystring(value) if isinstance(value, dict) else value) for key, value in dic.items()}

def innerdict_namecheck(count, dic):
    new_dict = {}
    for key, value in dic.items():
        if type(value) is dict:
            new_dict[key] = revise_keystring(count, value)
        else:
            new_dict[key] = value
    return new_dict

def dict_to_df_multi(param_dict_1, param_dict_4, time_dict, totaltime_dict, bool_dict):
    '''
    Match and merge two dictionaries (params/time) into one pandas dataframe. 
    The keys for each dictionary, #iter, represent the unique iter id's 
    for each experiment.
    Parameters:
        param_dict(dictionary): {#iter:{parameter_to_change:new_value}}
        time_dict(dictionary): {#iter:Albany_Total_Time}
    Returns:
        df(dataframe): pandas dataframe
    '''
    #print(param_dict)
    #print(time_dict)
    param_dict_1 = innerdict_namecheck(1, param_dict_1)
    #param_dict_3 = innerdict_namecheck(3, param_dict_3)
    param_dict_4 = innerdict_namecheck(4, param_dict_4)
    for key in param_dict_1:
        #if key in param_dict_3:
        #    param_dict_1[key].update(param_dict_3[key])
        if key in param_dict_4:
            param_dict_1[key].update(param_dict_4[key])
    for key, val in param_dict_1.items():
        param_dict_1[key]['time_NOX'] = time_dict[key]
        param_dict_1[key]['time_AlbanyTotal'] = totaltime_dict[key]
        param_dict_1[key]['passed'] = bool_dict[key]
    sorted_dict = sorted(param_dict_1.items(), key = lambda val: (val[1]["time_NOX"]))
    list_to_pd = list()
    for sorted_dic in sorted_dict:
        list_to_pd.append(sorted_dic[1])
    # print(list_to_pd)
    df = pd.DataFrame.from_dict(list_to_pd)
    return df

def dict_to_df_single(param_dict, time_dict, totaltime_dict, bool_dict):
    '''
    Match and merge two dictionaries (params/time) into one pandas dataframe.
    The keys for each dictionary, #iter, represent the unique iter id's
    for each experiment.
    Parameters:
        param_dict(dictionary): {#iter:{parameter_to_change:new_value}}
        time_dict(dictionary): {#iter:Albany_Total_Time}
    eturns:
        df(dataframe): pandas dataframe
    '''
    #print(param_dict)
    #print(time_dict)
    for key, val in param_dict.items():
        param_dict[key]['time_NOX'] = time_dict[key]
        param_dict[key]['time_AlbanyTotal'] = totaltime_dict[key]
        param_dict[key]['passed'] = bool_dict[key]
    sorted_dict = sorted(param_dict.items(), key = lambda val: (val[1]["time_NOX"]))
    list_to_pd = list()
    for sorted_dic in sorted_dict:
        list_to_pd.append(sorted_dic[1])
    # print(list_to_pd)
    df = pd.DataFrame.from_dict(list_to_pd)
    return df

def remove_files(yaml_filename):
    '''
    Remove previously-generated files: [input_yaml]_[#iter_id].yaml, *.log, ctest-*.json 
    from the current directory.
    Parameters:
        yaml_filename(string): the input yaml file name
    '''
    previous_yaml = yaml_filename.split('.')[0] + str("_*.yaml")
    prev_yaml = glob.glob(previous_yaml, recursive=False) #input_albany_Velocity_MueLu_Wedge_Tune_*.yaml 
    prev_log = glob.glob('*.log', recursive=False)
    prev_ctest = glob.glob('ctest-*', recursive=False) 
    for filePath in (prev_log + prev_yaml + prev_ctest): 
        try:
            os.remove(filePath)
        except OSError:
            print("Error while deleting file") 

###############################################################################
if __name__ == "__main__":
    '''
    Run experiments.
    '''
    yaml_filename = str()
  
    parser = argparse.ArgumentParser()
    parser.add_argument("yaml_input_file", type=str,
                    help="YAML input filename (with .yaml extension)")
    parser.add_argument("random_search_smoother", type=str,
                    help="Smoother(s): (single/multiple)")
    args = parser.parse_args()
    yaml_filename = args.yaml_input_file
    algo = args.random_search_smoother

    # Handle Wrong Input Argument format
    if not yaml_filename.endswith('.yaml'):
        parser.print_help()
        raise ValueError("The 2nd argument should be .yaml format")
    if algo not in ["single", "multiple"]:
        parser.print_help()
        raise ValueError("The 3rd argument should be chosen from single & multiple")

    print("YAML INPUT FILENAME: ", yaml_filename) 
    print("SEARCHING ALGORITHM: random ", algo)
    casename = get_casename(yaml_filename)
    pd_output = pd.DataFrame()

    if algo == "multiple":
        remove_files(yaml_filename)
        num_randsearch = int(input("RANDOM SEARCH #ITERS (integer>=1): "))
        seed = int(input("RANDOM SEARCH SEED (0<=integer<=2**32): "))
        # perform random search
        param1, param2 = random_search_multi(yaml_filename, num_randsearch, seed)
        # post process: get timers from generated json files
        out_filename = glob.glob('ctest-*.json')
        iter_time_dict, iter_totaltime_dict, iter_bool_dict = get_time_randomsearch(out_filename,casename)
        pd_output = dict_to_df_multi(param1, param2, iter_time_dict, iter_totaltime_dict, iter_bool_dict)

    else:
        remove_files(yaml_filename)
        num_randsearch = int(input("RANDOM SEARCH #ITERS (integer>=1): "))
        seed = int(input("RANDOM SEARCH SEED (0<=integer<=2**32): "))
        param = random_search_single(yaml_filename, num_randsearch, seed)
        out_filename = glob.glob('ctest-*.json')
        iter_time_dict, iter_totaltime_dict, iter_bool_dict = get_time_randomsearch(out_filename,casename)
        pd_output = dict_to_df_single(param, iter_time_dict, iter_totaltime_dict, iter_bool_dict)

    #pd_output = dict_to_df_multi(param1, param2, param3, iter_time_dict)
    print(pd_output)
    csv_out_str = os.path.splitext(yaml_filename)[0] + str('.csv')
    #print(csv_out_str)
    pd_output.to_csv(csv_out_str, index=False)
