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
def grid_search_multi(inFile, simu):
    '''
    Run experiment with parameter grid -- Grid Search. 
    Parameters:
        inFile(file): the input yaml file
        simu(integer): a nonneg integer that represents the current round of simulation
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
    #paramList = muDict['Factories']['mySmoother1']['ParameterList']
    paramList_1 = muDict['Factories']['mySmoother1']['ParameterList']
    paramList_4 = muDict['Factories']['mySmoother4']['ParameterList']
    
    TYPE = ['Two-stage Gauss-Seidel', 'MT Gauss-Seidel']
    DAMPING_FACTOR_1 = [0.25, 0.5, 0.75]
    SWEEP_1 = [1,2]
    SWEEP_4 = [2,4]

    # Define Grid: np.arange(start[inclusive], stop[exclusive], step)
    #DAMPING_FACTOR = list(np.arange(0.8, 1.2, 0.002).round(decimals=3))
    #SWEEPS = list(np.arange(1, 2, 1))
    param_grid_1 = {'relaxation: type': TYPE,
                    'relaxation: sweeps': SWEEP_1,
                    'relaxation: inner damping factor': DAMPING_FACTOR_1
                   }
    param_grid_4 = {'relaxation: type': TYPE,
                    'relaxation: sweeps': SWEEP_4
                   }

    grid_1 = ParameterGrid(param_grid_1)
    grid_4 = ParameterGrid(param_grid_4)

    #grid = ParameterGrid(param_grid)
    #print("TOTAL NUM OF CASES TO BE RUN: {}".format(len(list(grid))))
    
    # Run simulations
    ite = 0 # current #iter id
    iter_param_dict_1 = dict()
    iter_param_dict_4 = dict()
    for p1 in grid_1:
        dic1 = { key:((float)(round(value, 4)) if isinstance(value, float) else value) for key, value in p1.items() }
        paramList_1.update(dic1)
        for p4 in grid_4:
            print('\n')
            print("########################## CASE {} ##########################".format(ite))
            dic4 = { key:((float)(round(value, 4)) if isinstance(value, float) else value) for key, value in p4.items() }
            paramList_4.update(dic4)
            print("[mySmoother1] ", dic1)
            print("[mySmoother4] ", dic4) 
            write_yaml(inputDict, inFile)
            run_sim(ite, inFile)
            iter_param_dict_1.update({str(ite):p1})
            iter_param_dict_4.update({str(ite):p4})
            ite = ite + 1
    print('\n')
    print('######### TOTAL NUM OF CASES IN EACH SIMULATION: {} #########'.format(ite))
    print('#################### END OF SIMULATION {} ###################'.format(simu))
    # Convert logs to json
    run_bash('python ctest2json.py')
    return iter_param_dict_1, iter_param_dict_4

def grid_search_single(inFile, simu):
    '''
    Run experiment with parameter grid -- Grid Search. 
    Parameters:
        inFile(file): the input yaml file
        simu(integer): a nonneg integer that represents the current round of simulation
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
    
    # Define Grid: np.arange(start[inclusive], stop[exclusive], step)
    DAMPING_FACTOR = list(np.arange(0.8, 1.2, 0.002).round(decimals=3))
    SWEEPS = list(np.arange(1, 2, 1))
    param_grid = {'relaxation: damping factor': DAMPING_FACTOR,
                  'relaxation: sweeps': SWEEPS
                 # add more params here to tune if applicable
                 }
    grid = ParameterGrid(param_grid)
    print("TOTAL NUM OF CASES TO BE RUN: {}".format(len(list(grid))))
    
    # Run simulations
    ite = 0 # current #iter id
    iter_param_dict = dict()
    for params in grid:
        print('\n')
        print("########################## CASE {} ##########################".format(ite))
        # Change parameter
        for key, value in params.items():
            if key in paramList: 
                paramList[key] = value.item()
                print('{0}: {1}'.format(key, value.item()))
        iter_param_dict.update({str(ite):params})
        # Write input file
        write_yaml(inputDict, inFile)
        # Run yaml input file
        run_sim(ite, inFile)
        ite = ite + 1
    print('\n')
    print('######### TOTAL NUM OF CASES IN EACH SIMULATION: {} #########'.format(ite))
    print('#################### END OF SIMULATION {} ###################'.format(simu))
    # Convert logs to json
    run_bash('python ctest2json.py')
    return iter_param_dict

def get_time_gridsearch(filenames, case, simu, iter_time_dict):
    '''
    Return a dictionary with time extracted from the output json files.
    Parameters:
        filenames(list): a list that contains ctest-*.json in this directory
        case(string): a string that represents the targeted casename from output
        simu(integer): a nonneg integer that represents the current round of simulation
        iter_time_dict(dictionary): a passed-in dictionary {#iter:list(Albany_Total_Time)}
                                    in which the list of time needs to be updated
    Returns:
        iter_time_dict(dictionary): {#iter:list(Albany_Total_Time)} where
                                    #iter is the unique iter id for each experiment
                                    and the corresponding list of time is updated
    '''
    for each_file in filenames:
        with open(each_file) as f:
            dat = json.load(f)
            # ensure the test passed to get timer -- otherwise set to arbitrary large
            if dat.get(case, {}).get('passed') is True:
                time_linearsolve = dat.get(case, {}).get('timers', {}).get('NOX Total Linear Solve:')
                time_precondition = dat.get(case, {}).get('timers', {}).get('NOX Total Preconditioner Construction:')
                time = float(time_linearsolve) + float(time_precondition)
            else:
                time = float('inf')
            # extract time value and add to dictionary
            # output_num is the current #iter id
            output_num = each_file.split('-')[-1]
            output_num = os.path.splitext(output_num)[0]
            if simu == 0: 
                iter_time_dict[output_num] = list() # for the 1st time, initialize empty list
            iter_time_dict[output_num].append(time) # update the list of time
    return iter_time_dict

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

def dict_to_df_multi(param_dict_1, param_dict_4, time_dict):
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
        if key in param_dict_4:
            param_dict_1[key].update(param_dict_4[key])
    for key, val in param_dict_1.items():
        param_dict_1[key]['time_NOX'] = time_dict[key]
    sorted_dict = sorted(param_dict_1.items(), key = lambda val: (val[1]["time_NOX"]))
    list_to_pd = list()
    for sorted_dic in sorted_dict:
        list_to_pd.append(sorted_dic[1])
    # print(list_to_pd)
    df = pd.DataFrame.from_dict(list_to_pd)
    return df

def dict_to_df_single(param_dict, time_dict):
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
    for key, val in param_dict.items():
        param_dict[key]['time_NOX'] = time_dict[key]
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
    parser.add_argument("grid_search_smoother", type=str,
                    help="Smoother(s): (single/multiple)")
    args = parser.parse_args()
    yaml_filename = args.yaml_input_file
    algo = args.grid_search_smoother

    # Handle Wrong Input Argument format
    if not yaml_filename.endswith('.yaml'):
        parser.print_help()
        raise ValueError("The 2nd argument should be .yaml format")
    if algo not in ["single", "multiple"]:
        parser.print_help()
        raise ValueError("The 3rd argument should be chosen from single & multiple")

    print("YAML INPUT FILENAME: ", yaml_filename) 
    print("SEARCHING ALGORITHM: grid, ", algo)
    casename = get_casename(yaml_filename)
    pd_output = pd.DataFrame()

    if algo == "multiple":
        num_simu = int(input("#ROUNDS OF SIMULATIONS (integer>=1): "))
        iter_time_dict = dict()
        for i in range(num_simu):
            remove_files(yaml_filename)
            # perform grid search
            print('\n')
            print("####################### SIMULATION {} #######################".format(i))
            param1, param2 = grid_search_multi(yaml_filename, i)
            # post process: get timers from generated json files
            out_filename = glob.glob('ctest-*.json')
            iter_time_dict = get_time_gridsearch(out_filename, casename, i, iter_time_dict)
            #print("ITER TIME DICT: ", iter_time_dict)
        # take median of time from all rounds
        iter_time_dict = {k: statistics.median(time_list) for k, time_list in iter_time_dict.items()}
        # round final digits to 4
        iter_time_dict = {k: round(iter_time_dict[k], 4) for k in iter_time_dict}
        #print("FINAL: ", iter_time_dict)
        pd_output = dict_to_df_multi(param1, param2, iter_time_dict)
    
    else: # single
        num_simu = int(input("#ROUNDS OF SIMULATIONS (integer>=1): "))
        iter_time_dict = dict()
        for i in range(num_simu):
            remove_files(yaml_filename)
            print('\n')
            print("####################### SIMULATION {} #######################".format(i))
            param = grid_search_single(yaml_filename, i)
            out_filename = glob.glob('ctest-*.json')
            iter_time_dict = get_time_gridsearch(out_filename, casename, i, iter_time_dict)
        iter_time_dict = {k: statistics.median(time_list) for k, time_list in iter_time_dict.items()}
        iter_time_dict = {k: round(iter_time_dict[k], 4) for k in iter_time_dict}
        pd_output = dict_to_df_single(param, iter_time_dict)

    # get parameters with corresponding time in ascending order
    print(pd_output)
    csv_out_str = os.path.splitext(yaml_filename)[0] + str('.csv')
    #print(csv_out_str)
    pd_output.to_csv(csv_out_str, index=False)
