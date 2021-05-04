# Warning: The execution of this file will automatically remove *.log, 
#          ctest-*.json and all auto-generated _[X].yaml files from this directory.
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
import subprocess
import sys
from collections import Counter
from sklearn.model_selection import ParameterGrid
from ruamel.yaml import YAML

yaml = YAML(typ='rt')  # Round trip loading and dumping
yaml.preserve_quotes = True
yaml.width = 1000

def read_yaml(filename):
    with open(filename) as file:
        dictionary = yaml.load(file)
    return dictionary

def write_yaml(dictionary, filename):
    with open(filename, 'w') as file:
        yaml.dump(dictionary, file)
        file.write('...\n')

###################################################################################################
def run_bash(command):
    '''
    Run a bash command
    '''
    return subprocess.run(command, shell=True, executable='/bin/bash')

###################################################################################################
def run_sim(iter, inFile):
    '''
    Run yaml input file
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
    run_bash('ctest -L "tune" --timeout 60')

    # Generate input file
    newInFile = inFile.split('.')[0] + '_' + str(iter) + '.' + inFile.split('.')[1]
    run_bash('cp ' + inFile + ' ' + newInFile)

    # Generate output file
    run_bash('cp Testing/Temporary/LastTest.log LastTest_'+str(iter)+'-0.log')

###################################################################################################

def grid_search(inFile):
    '''
    Run multiple sims with parameter grid.
    Parameters:
        inFile(file): the input yaml file
    Returns:
        iter_param_dict(dictionary): {#iter:{parameter_to_change:new_value}}
    '''
    # Read input file
    inputDict = read_yaml(inFile)

    # Extract MueLu dictionary
    linsolDict = inputDict['ANONYMOUS']['Piro']['NOX']['Direction']['Newton']['Stratimikos Linear Solver']
    muDict = linsolDict['Stratimikos']['Preconditioner Types']['MueLu']

    # Parameter to change
    paramList = muDict['Factories']['mySmoother1']['ParameterList']
    
    # Define Grid: np.arange(start[inclusive], stop[exclusive], step)
    param_grid = {'relaxation: damping factor': list(np.arange(0.8, 1.0, 0.1).round(decimals=1)),
                  'relaxation: sweeps': list(np.arange(1, 2, 1))
                 # add more params here to tune if applicable
                 }
    grid = ParameterGrid(param_grid)
    
    # Run simulations
    ite = 0
    iter_param_dict = dict()
    for params in grid:
        # Change parameter
        for key, value in params.items():
            if key in paramList: paramList[key] = value.item()
        iter_param_dict.update({str(ite):params})
        # Write input file
        write_yaml(inputDict, inFile)
        # Run yaml input file
        run_sim(ite, inFile)
        ite = ite + 1
    print('Total #iterations (cases):', ite)
    # Convert logs to json
    run_bash('python ctest2json.py')
    return iter_param_dict

def json_timers(filenames, case):
    '''
    Return a dictionary with time from output json files
    Parameters:
        filenames(list): a list that contains ctest-*.json in this directory
        case(string): a string that represents the targeted casename from output
    Returns:
        iter_time_dict(dictionary): {#iter:Albany_Total_Time}
    '''
    #print("CASE: ", case)
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
            output_num = each_file.split('-')[-1]
            output_num = os.path.splitext(output_num)[0]
            iter_time_dict.update({output_num:time})
    return iter_time_dict

def get_casename(yamlfile):
    '''
    Get the corresponding casename from cmake file to minimize hardcoding
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

def dict_to_pandas(param_dict, time_dict):
    '''
    Merge two dictionaries (params/time) into one pandas dataframe
    Parameters:
        param_dict(dictionary): {#iter:{parameter_to_change:new_value}}
        time_dict(dictionary): {#iter:Albany_Total_Time}
    Returns:
        df(dataframe): pandas dataframe
    '''
    for key, val in param_dict.items():
        param_dict[key]['time'] = time_dict[key]
    sorted_dict = sorted(param_dict.items(), key = lambda val: (val[1]["time"]))
    list_to_pd = list()
    for sorted_dic in sorted_dict:
        list_to_pd.append(sorted_dic[1])
    # print(list_to_pd)
    df = pd.DataFrame.from_dict(list_to_pd)
    return df
###################################################################################################
if __name__ == "__main__":
    '''
    Run example
    '''

    yaml_filename = str()
    num_simu = 1
  
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str,
                    help="YAML input filename")
    parser.add_argument("-s", "--simulations", type=int,
                    help="Number of sampled simulations [Default=1]")
    args = parser.parse_args()
    yaml_filename = args.filename
    if args.simulations:
        num_simu = args.simulations
    print("YAML INPUT FILENAME: ", yaml_filename) 
    print("NUM OF SIMULATION(s): ", num_simu)

    casename = get_casename(yaml_filename)

    iter_time_dict = dict()
    for i in range(num_simu):
        # remove previously-generated files: Tune_*.yaml, *.log, ctest-*.json from this directory
        previous_yaml = yaml_filename.split('.')[0] + str("_*.yaml")
        prev_yaml = glob.glob(previous_yaml, recursive=False) #input_albany_Velocity_MueLu_Wedge_Tune_*.yaml 
        prev_log = glob.glob('*.log', recursive=False)
        prev_ctest = glob.glob('ctest-*', recursive=False)
        for filePath in (prev_log + prev_yaml + prev_ctest): 
            try:
                os.remove(filePath)
            except OSError:
                print("Error while deleting file")
        # perform grid search
        print('\n')
        print("############SIMULATION {}############".format(i))
        iter_param_dict = grid_search(yaml_filename)
        # post process: get timers from generated json files
        out_filename = glob.glob('ctest-*.json')
        if i != 0:
            old_dict = iter_time_dict
            new_dict = json_timers(out_filename,casename)
            iter_time_dict = dict(Counter(old_dict)+Counter(new_dict))
        else: 
            iter_time_dict = json_timers(out_filename,casename)
        #print("ITER_TIME_DICT: ", iter_time_dict)
    iter_time_dict = {k: v/(num_simu) for k, v in iter_time_dict.items()}
    iter_time_dict = {k: round(iter_time_dict[k], 4) for k in iter_time_dict}
    #print("FINAL: ", iter_time_dict)
    # get parameters with corresponding time in ascending order
    pd_output = dict_to_pandas(iter_param_dict, iter_time_dict)
    print(pd_output)
    csv_out_str = os.path.splitext(yaml_filename)[0] + str('.csv')
    # print(csv_out_str)
    pd_output.to_csv(csv_out_str, index=False)
