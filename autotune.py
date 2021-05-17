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
def grid_search(inFile, simu):
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
    paramList_3 = muDict['Factories']['mySmoother3']['ParameterList']
    paramList_4 = muDict['Factories']['mySmoother4']['ParameterList']
    
    TYPE = ['Two-stage Gauss-Seidel', 'MT Gauss-Seidel']
    DAMPING_FACTOR_1 = [0.25, 0.5, 0.75]
    SWEEP_1 = [1,2]
    DAMPING_FACTOR_3 = [0.8, 1.0]
    SWEEP_3 = [1,2]
    SWEEP_4 = [2,4]

    # Define Grid: np.arange(start[inclusive], stop[exclusive], step)
    #DAMPING_FACTOR = list(np.arange(0.8, 1.2, 0.002).round(decimals=3))
    #SWEEPS = list(np.arange(1, 2, 1))
    param_grid_1 = {'relaxation: type': TYPE,
                    'relaxation: sweeps': SWEEP_1,
                    'relaxation: inner damping factor': DAMPING_FACTOR_1
                   }
    param_grid_3 = {'relaxation: type': TYPE,
                    'relaxation: sweeps': SWEEP_3,
                    'relaxation: damping factor': DAMPING_FACTOR_3
                   }
    param_grid_4 = {'relaxation: type': TYPE,
                    'relaxation: sweeps': SWEEP_4
                   }

    grid_1 = ParameterGrid(param_grid_1)
    grid_3 = ParameterGrid(param_grid_3)
    grid_4 = ParameterGrid(param_grid_4)

    #grid = ParameterGrid(param_grid)
    #print("TOTAL NUM OF CASES TO BE RUN: {}".format(len(list(grid))))
    
    # Run simulations
    ite = 0 # current #iter id
    iter_param_dict_1 = dict()
    iter_param_dict_3 = dict()
    iter_param_dict_4 = dict()
    for p1 in grid_1:
        dic1 = { key:((float)(round(value, 4)) if isinstance(value, float) else value) for key, value in p1.items() }
        paramList_1.update(dic1)
        for p3 in grid_3:
            dic3 = { key:((float)(round(value, 4)) if isinstance(value, float) else value) for key, value in p3.items() }
            paramList_3.update(dic3)
            for p4 in grid_4:
                print('\n')
                print("########################## CASE {} ##########################".format(ite))
                dic4 = { key:((float)(round(value, 4)) if isinstance(value, float) else value) for key, value in p4.items() }
                paramList_4.update(dic4)
                print("[mySmoother1] ", dic1)
                print("[mySmoother3] ", dic3)
                print("[mySmoother4] ", dic4) 
                write_yaml(inputDict, inFile)
                run_sim(ite, inFile)
                iter_param_dict_1.update({str(ite):p1})
                iter_param_dict_3.update({str(ite):p3})
                iter_param_dict_4.update({str(ite):p4})
                ite = ite + 1
    print('\n')
    print('######### TOTAL NUM OF CASES IN EACH SIMULATION: {} #########'.format(ite))
    print('#################### END OF SIMULATION {} ###################'.format(simu))
    # Convert logs to json
    run_bash('python ctest2json.py')
    return iter_param_dict_1, iter_param_dict_3, iter_param_dict_4

def grid_search_old(inFile, simu):
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

def random_search(inFile, n_iter, seed):
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
    paramList_3 = muDict['Factories']['mySmoother3']['ParameterList']
    paramList_4 = muDict['Factories']['mySmoother4']['ParameterList']

    # Define Random State with the Mersenne Twister pseudo-random number generator
    random_state = np.random.RandomState(seed)

    TYPE = ['Two-stage Gauss-Seidel', 'MT Gauss-Seidel']
    DAMPING_FACTOR_1 = get_truncated_normal(0.5, 0.4, 0.0, 1.0)
    SWEEP_1 = list(range(1, 3))
    DAMPING_FACTOR_3 = get_truncated_normal(0.8, 0.3, 0.4, 1.2)
    SWEEP_3 = list(range(1, 3))
    SWEEP_4 = list(range(1, 5))

    param_grid_1 = {'relaxation: type': TYPE,
                    'relaxation: sweeps': SWEEP_1,
                    'relaxation: inner damping factor': DAMPING_FACTOR_1
                   }
    param_grid_3 = {'relaxation: type': TYPE,
                    'relaxation: sweeps': SWEEP_3,
                    'relaxation: damping factor': DAMPING_FACTOR_3
                   }
    param_grid_4 = {'relaxation: type': TYPE,
                    'relaxation: sweeps': SWEEP_4
                   }

    grid_1 = ParameterSampler(param_grid_1, n_iter=n_iter, random_state=random_state)
    grid_3 = ParameterSampler(param_grid_3, n_iter=n_iter, random_state=random_state)
    grid_4 = ParameterSampler(param_grid_4, n_iter=n_iter, random_state=random_state)
    
    param_1 = [dict((k, v) for (k, v) in d.items()) for d in grid_1]
    param_3 = [dict((k, v) for (k, v) in d.items()) for d in grid_3]
    param_4 = [dict((k, v) for (k, v) in d.items()) for d in grid_4]

    param_1 = [{ k: float(round(v,4)) if isinstance(v,float) else v for k,v in x.items()} for x in param_1]
    param_3 = [{ k: float(round(v,4)) if isinstance(v,float) else v for k,v in x.items()} for x in param_3]
    param_4 = [{ k: float(round(v,4)) if isinstance(v,float) else v for k,v in x.items()} for x in param_4]

    #grid = ParameterGrid(param_grid)
    #print("TOTAL NUM OF CASES TO BE RUN: {}".format(len(list(grid))))
    
    # Run simulations
    #ite = 0 # current #iter id
    iter_param_dict_1 = dict()
    iter_param_dict_3 = dict()
    iter_param_dict_4 = dict()
    
    for i in range(len(param_1)):
        print('\n')
        print("########################## CASE {} ##########################".format(i))
        paramList_1.update(param_1[i])
        print("[mySmoother1] ", param_1[i])
        paramList_3.update(param_3[i])
        print("[mySmoother3] ", param_3[i])
        paramList_4.update(param_4[i])
        print("[mySmoother4] ", param_4[i])

        write_yaml(inputDict, inFile)
        run_sim(i, inFile)
        
        iter_param_dict_1.update({str(i):param_1[i]})
        iter_param_dict_3.update({str(i):param_3[i]})
        iter_param_dict_4.update({str(i):param_4[i]})
        #ite = ite + 1
        
    print('\n')
    print('################### TOTAL NUM OF CASES: {} ##################'.format(len(param_1)))
    run_bash('python ctest2json.py')
    return iter_param_dict_1, iter_param_dict_3, iter_param_dict_4

def random_search_old(inFile, n_iter, seed):
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
    for each_file in filenames:
        with open(each_file) as f:
            dat = json.load(f)
            # ensure the test passed to get timer -- otherwise set to arbitrary large
            if dat.get(case, {}).get('passed') is True:
                time = dat.get(case, {}).get('timers', {}).get('Albany Total Time:')
            else:
                time = float('inf')
            # extract time value and add to dictionary
            # output_num is the current #iter id 
            output_num = each_file.split('-')[-1]
            output_num = os.path.splitext(output_num)[0]
            iter_time_dict.update({output_num:time})
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

def transform(count, dic):
    return { str(count)+'::'+str(key) : (transform(value) if isinstance(value, dict) else value) for key, value in dic.items()}

def copydict(count, dic):
    new_dict = {}
    for key, value in dic.items():
        if type(value) is dict:
            new_dict[key] = transform(count, value)
        else:
            new_dict[key] = value
    return new_dict

def dict_to_pandas(param_dict_1, param_dict_3, param_dict_4, time_dict):
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
    param_dict_1 = copydict(1, param_dict_1)
    param_dict_3 = copydict(3, param_dict_3)
    param_dict_4 = copydict(4, param_dict_4)
    for key in param_dict_1:
        if key in param_dict_3:
            param_dict_1[key].update(param_dict_3[key])
        if key in param_dict_4:
            param_dict_1[key].update(param_dict_4[key])
    for key, val in param_dict_1.items():
        param_dict_1[key]['time'] = time_dict[key]
    sorted_dict = sorted(param_dict_1.items(), key = lambda val: (val[1]["time"]))
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
    parser.add_argument("filename", type=str,
                    help="YAML input filename (.yaml)")
    parser.add_argument("search", type=str,
                    help="Searching algorithm (grid/random)")
    args = parser.parse_args()
    yaml_filename = args.filename
    algo = args.search
    print("YAML INPUT FILENAME: ", yaml_filename) 
    print("SEARCHING ALGORITHM: ", algo)
    casename = get_casename(yaml_filename)

    # GRID SEARCH
    if algo == "grid":
        num_simu = int(input("#ROUNDS OF SIMULATIONS (integer>=1): "))
        iter_time_dict = dict()
        for i in range(num_simu):
            remove_files(yaml_filename)
            # perform grid search
            print('\n')
            print("####################### SIMULATION {} #######################".format(i))
            param1, param2, param3 = grid_search(yaml_filename, i)
            # post process: get timers from generated json files
            out_filename = glob.glob('ctest-*.json')
            iter_time_dict = get_time_gridsearch(out_filename, casename, i, iter_time_dict)
            #print("ITER TIME DICT: ", iter_time_dict)
        # take median of time from all rounds
        iter_time_dict = {k: statistics.median(time_list) for k, time_list in iter_time_dict.items()}
        # round final digits to 4
        iter_time_dict = {k: round(iter_time_dict[k], 4) for k in iter_time_dict}
        #print("FINAL: ", iter_time_dict)
    # RANDOM SEARCH
    else: 
        remove_files(yaml_filename)
        num_randsearch = int(input("RANDOM SEARCH #ITERS (integer>=1): "))
        seed = int(input("RANDOM SEARCH SEED (0<=integer<=2**32): "))
        # perform random search
        param1, param2, param3 = random_search(yaml_filename, num_randsearch, seed)
        # post process: get timers from generated json files
        out_filename = glob.glob('ctest-*.json')
        iter_time_dict = get_time_randomsearch(out_filename,casename)

    # get parameters with corresponding time in ascending order
    pd_output = dict_to_pandas(param1, param2, param3, iter_time_dict)
    print(pd_output)
    csv_out_str = os.path.splitext(yaml_filename)[0] + str('.csv')
    #print(csv_out_str)
    pd_output.to_csv(csv_out_str, index=False)
