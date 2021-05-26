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

def run_bash(command):
    return subprocess.run(command, shell=True, executable='/bin/bash')

def read_yaml(filename):
    with open(filename) as f:
        dictionary = yaml.load(f)
    return dictionary

def write_yaml(dictionary, filename):
    with open(filename, 'w') as f:
        yaml.dump(dictionary, f)
        f.write('...\n')

def check_json(filename, casename):
    with open(filename) as f:
        dictionary = json.load(f)
        casename_check =  casename in dictionary
    return casename_check

def merge_dict(dict1, dict2, dict3, dict4):
    m = {**dict1, **dict2, **dict3, **dict4}
    return m

def revise_keystring(count, dic):
    return { str(count)+'::'+str(key) : (revise_keystring(value) if isinstance(value, dict) else value) for key, value in dic.items()}

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

def random_search(inFile, iter_id, properties_file):
    inputDict = read_yaml(inFile)

    # Extract MueLu dictionary
    linsolDict = inputDict['ANONYMOUS']['Piro']['NOX']['Direction']['Newton']['Stratimikos Linear Solver']
    muDict = linsolDict['Stratimikos']['Preconditioner Types']['MueLu']

    # Parameter to change
    paramList_1 = muDict['Factories']['mySmoother1']['ParameterList']
    paramList_4 = muDict['Factories']['mySmoother4']['ParameterList']

    # Define Random State with the Mersenne Twister pseudo-random number generator
    random_state = np.random.RandomState()

    try:
        with open(properties_file) as prop:
            dic_prop = json.load(prop)
            mS1 = dic_prop['mS1']
            mS4 = dic_prop['mS4']

            TYPE_1 = mS1['relaxation: type']
            SWEEP_1 = mS1['relaxation: sweeps']
            damping_1 = mS1['relaxation: inner damping factor']
            DAMPING_1 = get_truncated_normal(damping_1['mean'], damping_1['sd'], damping_1['low'], damping_1['upper'])

            TYPE_4 = mS4['relaxation: type']
            SWEEP_4 = mS4['relaxation: sweeps']
    except IOError:
        print("File not accessible")

    param_grid_1 = {'relaxation: type': TYPE_1,
                    'relaxation: sweeps': SWEEP_1,
                    'relaxation: inner damping factor': DAMPING_1
                   }
    param_grid_4 = {'relaxation: type': TYPE_4,
                    'relaxation: sweeps': SWEEP_4
                   }
    grid_1 = ParameterSampler(param_grid_1, n_iter=1, random_state=random_state)
    grid_4 = ParameterSampler(param_grid_4, n_iter=1, random_state=random_state)
    
    param_1 = [dict((k, v) for (k, v) in d.items()) for d in grid_1]
    param_4 = [dict((k, v) for (k, v) in d.items()) for d in grid_4]

    param_1 = [{ k: float(round(v,4)) if isinstance(v,float) else v for k,v in x.items()} for x in param_1]
    param_4 = [{ k: float(round(v,4)) if isinstance(v,float) else v for k,v in x.items()} for x in param_4]

    # Run simulations
    iter_param_dict_1 = dict()
    iter_param_dict_4 = dict()
    
    for i in range(len(param_1)):
        print('\n')
        paramList_1.update(param_1[i])
        print("[mySmoother1] ", param_1[i])
        paramList_4.update(param_4[i])
        print("[mySmoother4] ", param_4[i])

        write_yaml(inputDict, inFile)
        #run_sim(i, inFile)
        
        iter_id = {'iter_id': iter_id}
        iter_param_dict_1 = param_1[i]
        iter_param_dict_4 = param_4[i]
        iter_param_dict_1 = revise_keystring(1, iter_param_dict_1)
        iter_param_dict_4 = revise_keystring(4, iter_param_dict_4)
        iter_time = {'time_NOX': None, 'time_AlbanyTotal': None, 'passed': None}
        merged = merge_dict(iter_id, iter_param_dict_1, iter_param_dict_4, iter_time)
    #run_bash('python ctest2json.py')
    return merged

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("yaml_input_file", type=str, help="YAML input filename (w/.yaml extension)")
    parser.add_argument("ctest_output_file", type=str, help="ctest output filename (w/.json extension)")
    parser.add_argument("casename", type=str, help="casename")
    args = parser.parse_args()
    
    yaml_filename = args.yaml_input_file
    ctest_filename = args.ctest_output_file
    case_name = args.casename
    csv_hist = case_name + str("_hist.csv")
    yaml_best = yaml_filename.split('.')[0] + '_' + 'Best' + '.' + yaml_filename.split('.')[1]

    if not yaml_filename.endswith('.yaml'):
        parser.print_help()
        sys.exit(2)
    if not ctest_filename.endswith('.json'):
        parser.print_help()
        sys.exit(2)

    properties_json = '_properties.json'

    ite_count = -1

    # Check to see if a history file exists
    # If not, open and write to a new file with input params by calling random search
    if not os.path.isfile(csv_hist):
        # run random search, update yaml file
        ite_count = 0
        merged = random_search(yaml_filename, ite_count, properties_json)
        #print(merged)
        df = pd.DataFrame.from_records([merged])
        df.to_csv(csv_hist, index=False)
        # let the new yaml file be the best
        yaml_ite = yaml_filename.split('.')[0] + '_' + str(ite_count) + '.' + yaml_filename.split('.')[1]
        run_bash('cp ' + yaml_filename + ' ' + yaml_ite)
        run_bash('cp ' + yaml_ite + ' ' + yaml_best)
        print(df)
    # If exists, open ctest json file and read timer
    else:
        hist_df = pd.read_csv(csv_hist)
        case = check_json(ctest_filename, case_name)
        with open(ctest_filename) as f_ctest:
            dict_ctest = json.load(f_ctest)
            casename_check = case_name in dict_ctest
            if casename_check == False: raise ValueError("The casename is not found in the ctest output file")
            if dict_ctest.get(case_name, {}).get('passed') is True: 
                time_linearsolve = dict_ctest.get(case_name, {}).get('timers', {}).get('NOX Total Linear Solve:')
                time_precondition = dict_ctest.get(case_name, {}).get('timers', {}).get('NOX Total Preconditioner Construction:')
                time = float(time_linearsolve) + float(time_precondition)
                totaltime = dict_ctest.get(case_name, {}).get('timers', {}).get('Albany Total Time:')
                # append timer entry to csv
                hist_df.loc[hist_df.index[-1], 'time_NOX']= time
                hist_df.loc[hist_df.index[-1], 'time_AlbanyTotal']= totaltime
                hist_df.loc[hist_df.index[-1], 'passed'] = True
                #print(hist_df)
            else: # NOT PASS
                hist_df.loc[hist_df.index[-1], 'time_NOX']= float('inf')
                hist_df.loc[hist_df.index[-1], 'time_AlbanyTotal']= float('inf')
                hist_df.loc[hist_df.index[-1], 'passed'] = False
            # extract #iteration count
            ite_count = hist_df.iloc[-1]['iter_id']

            # from the hist file, find the best param combo, from properties update best yaml
            min_index = hist_df['time_NOX'].idxmin()
            min_iteid = hist_df.iloc[min_index]['iter_id']
            yaml_ite = yaml_filename.split('.')[0] + '_' + str(min_iteid) + '.' + yaml_filename.split('.')[1]
            run_bash('cp ' + yaml_ite + ' ' + yaml_best)

        # run random search, update yaml file for the next round
        ite_count = ite_count + 1
        merged = random_search(yaml_filename, ite_count, properties_json)
        hist_df = hist_df.append(merged, ignore_index=True)
        print(hist_df)
        hist_df.to_csv(csv_hist, index=False)
        yaml_ite = yaml_filename.split('.')[0] + '_' + str(ite_count) + '.' + yaml_filename.split('.')[1]
        run_bash('cp ' + yaml_filename + ' ' + yaml_ite)  
        
if __name__ == "__main__":
    main()
