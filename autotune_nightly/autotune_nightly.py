import argparse
import json
import numpy as np
import os
import pandas as pd
import random
import statistics
import subprocess
import sys
from scipy.stats import truncnorm
from sklearn.model_selection import ParameterSampler
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

def randomtype_generator(properties_file):
    mS1_types = list()
    mS4_types = list()
    try:
        with open(properties_file) as prop:
            dic_prop = json.load(prop)
            mS1_types = dic_prop['mS1']['type_options']
            mS4_types = dic_prop['mS4']['type_options']
    except IOError:
        print("File not accessible")
    mS1_type = random.choice(mS1_types)
    mS4_type = random.choice(mS4_types)
    return mS1_type, mS4_type

def paramdict_generator(mySmoother, mS_type, properties_file):
    param_dict = dict()
    category = str()
    if mS_type == "MT Gauss-Seidel":
        try:
            with open(properties_file) as prop:
                dic_prop = json.load(prop)
                sweep = dic_prop[mySmoother]['relaxation: sweeps']
                SWEEP = list(range(sweep['inclusive_lower_bound'], sweep['inclusive_upper_bound']+1))
                damping = dic_prop[mySmoother]['relaxation: damping factor']
                DAMPING = get_truncated_normal(damping['mean'], damping['sd'], damping['low'], damping['upper'])
        except IOError:
            print("File not accessible")
        param_dict = {'relaxation: type': [mS_type],
                      'relaxation: sweeps': SWEEP, 
                      'relaxation: damping factor': DAMPING}
        category = "RELAXATION"
    elif mS_type == "Two-stage Gauss-Seidel":
        try:
            with open(properties_file) as prop:
                dic_prop = json.load(prop)
                sweep = dic_prop[mySmoother]['relaxation: sweeps']
                SWEEP = list(range(sweep['inclusive_lower_bound'], sweep['inclusive_upper_bound']+1))
                damping = dic_prop[mySmoother]['relaxation: inner damping factor']
                DAMPING = get_truncated_normal(damping['mean'], damping['sd'], damping['low'], damping['upper'])
        except IOError:
            print("File not accessible")
        param_dict = {'relaxation: type': [mS_type],
                      'relaxation: sweeps': SWEEP, 
                      'relaxation: inner damping factor': DAMPING}
        category = "RELAXATION"
    elif mS_type == "CHEBYSHEV":
        try:
            with open(properties_file) as prop:
                dic_prop = json.load(prop)
                degree = dic_prop[mySmoother]['chebyshev: degree']
                DEGREE = list(range(degree['inclusive_lower_bound'], degree['inclusive_upper_bound']+1))
                ratio_eval = dic_prop[mySmoother]['chebyshev: ratio eigenvalue']
                RATIO_EVAL = get_truncated_normal(ratio_eval['mean'], ratio_eval['sd'], ratio_eval['low'], ratio_eval['upper'])
                eval_maxit = dic_prop[mySmoother]['chebyshev: eigenvalue max iterations']
                EVAL_MAXIT = list(range(eval_maxit['inclusive_lower_bound'], eval_maxit['inclusive_upper_bound']+1))
        except IOError:
            print("File not accessible")
        param_dict = {'chebyshev: degree': DEGREE,
                      'chebyshev: ratio eigenvalue': RATIO_EVAL, 
                      'chebyshev: eigenvalue max iterations': EVAL_MAXIT}
        category = "CHEBYSHEV"
    else:
        raise ValueError("Type options are not defined by MT Gauss-Seidel, Two-stage Gauss-Seidel or CHEBYSHEV")

    return category, param_dict
        
    
def random_search(inFile, iter_id, properties_file):
    inputDict = read_yaml(inFile)

    # Extract MueLu dictionary
    linsolDict = inputDict['ANONYMOUS']['Piro']['NOX']['Direction']['Newton']['Stratimikos Linear Solver']
    muDict = linsolDict['Stratimikos']['Preconditioner Types']['MueLu']

    # Parameter to change
    paramList_1 = muDict['Factories']['mySmoother1']
    paramList_4 = muDict['Factories']['mySmoother4']

    TYPE_1, TYPE_4 = randomtype_generator(properties_file)
    CATE_1, PARAMDICT_1 = paramdict_generator("mS1", TYPE_1, properties_file)
    CATE_4, PARAMDICT_4 = paramdict_generator("mS4", TYPE_4, properties_file)

    # Define Random State with the Mersenne Twister pseudo-random number generator

    sample_1 = ParameterSampler(PARAMDICT_1, n_iter=1, random_state=np.random.RandomState())
    sample_4 = ParameterSampler(PARAMDICT_4, n_iter=1, random_state=np.random.RandomState())
    
    param_1 = [dict((k, v) for (k, v) in d.items()) for d in sample_1]
    param_4 = [dict((k, v) for (k, v) in d.items()) for d in sample_4]
    param_1 = [{ k: float(round(v,4)) if isinstance(v,float) else v for k,v in x.items()} for x in param_1]
    param_4 = [{ k: float(round(v,4)) if isinstance(v,float) else v for k,v in x.items()} for x in param_4]

    # Run simulations
    #iter_param_dict_1 = dict()
    #iter_param_dict_4 = dict()
    
    # MS1
    p1 = param_1[0]
    paramList_1['type'] = CATE_1
    paramList_1['ParameterList'].clear()
    paramList_1['ParameterList'].update(p1)

    # MS4
    p4 = param_4[0]
    paramList_4['type'] = CATE_4
    paramList_4['ParameterList'].clear()
    paramList_4['ParameterList'].update(p4)
    
    print("[mySmoother1] ", param_1[0])
    print("[mySmoother4] ", param_4[0])
    print('\n')
    write_yaml(inputDict, inFile) 

    iter_id = {'iter_id': iter_id} 
    p1 = revise_keystring(1, p1)
    p4 = revise_keystring(4, p4)

    iter_time = {'time_NOX': None, 'time_AlbanyTotal': None, 'passed': None}
    merged = merge_dict(iter_id, p1, p4, iter_time)

    return merged

def sort_pd_col(df):
    col_list = list(df.columns)
    ordering_rule = ['iter_id', 
                     '1::relaxation: type', 
                     '1::relaxation: sweeps', 
                     '1::relaxation: damping factor', 
                     '1::relaxation: inner damping factor',
                     '1::chebyshev: degree',
                     '1::chebyshev: ratio eigenvalue',
                     '1::chebyshev: eigenvalue max iterations',
                     '4::relaxation: type', 
                     '4::relaxation: sweeps', 
                     '4::relaxation: damping factor', 
                     '4::relaxation: inner damping factor',
                     '4::chebyshev: degree',
                     '4::chebyshev: ratio eigenvalue',
                     '4::chebyshev: eigenvalue max iterations',
                     'time_NOX',
                     'time_AlbanyTotal',
                     'passed'
                    ]
    ordered_col_list = [name for name in ordering_rule if name in col_list]
    df = df[ordered_col_list]
    return df

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("properties_file", type=str, help="parameter space definition (.json)")
    parser.add_argument("ctest_output_file", type=str, help="ctest output filename (.json)")
    args = parser.parse_args()
    
    yaml_filename = str()
    ctest_filename = args.ctest_output_file
    case_name = str()

    properties_json = args.properties_file
    try:
        with open(properties_json) as prop:
            dic_prop = json.load(prop)
            yaml_filename = dic_prop['input']
            case_name = dic_prop['case']

    except IOError:
        print("File not accessible")

    csv_hist = case_name + str("_hist.csv")
    csv_hist_sorted = case_name + str("_hist_sorted.csv")
    yaml_best = yaml_filename.split('.')[0] + '_' + 'Best' + '.' + yaml_filename.split('.')[1]

    if not yaml_filename.endswith('.yaml'):
        parser.print_help()
        sys.exit(2)
    if not ctest_filename.endswith('.json'):
        parser.print_help()
        sys.exit(2)
    if not properties_json.endswith('.json'):
        parser.print_help()
        sys.exit(2)

    ite_count = -1

    # Check to see if a history file exists
    # If not, open and write to a new file with input params by calling random search
    if not os.path.isfile(csv_hist):
        # run random search, update yaml file
        ite_count = 0
        merged = random_search(yaml_filename, ite_count, properties_json)
        #print(merged)
        df = pd.DataFrame.from_records([merged])
        df = sort_pd_col(df)
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
                try:
                    time_linearsolve = dict_ctest.get(case_name, {}).get('timers', {}).get('NOX Total Linear Solve:')
                    time_precondition = dict_ctest.get(case_name, {}).get('timers', {}).get('NOX Total Preconditioner Construction:')
                    time = float(time_linearsolve) + float(time_precondition)
                    totaltime = dict_ctest.get(case_name, {}).get('timers', {}).get('Albany Total Time:')
                    # append timer entry to csv
                    hist_df.loc[hist_df.index[-1], 'time_NOX']= time
                    hist_df.loc[hist_df.index[-1], 'time_AlbanyTotal']= totaltime
                    hist_df.loc[hist_df.index[-1], 'passed'] = True
                    #print(hist_df)
                except TypeError:
                    print("Make sure NOX and Albany timers are accessible for case {0} under {1}".format(case_name, ctest_filename))
                    
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
        hist_df = sort_pd_col(hist_df)
        print(hist_df)
        hist_df.to_csv(csv_hist, index=False)
        sorted_hist_df = hist_df.sort_values(by=['time_NOX'], ascending=True)
        sorted_hist_df.to_csv(csv_hist_sorted, index=False)
        yaml_ite = yaml_filename.split('.')[0] + '_' + str(ite_count) + '.' + yaml_filename.split('.')[1]
        run_bash('cp ' + yaml_filename + ' ' + yaml_ite)  
        
if __name__ == "__main__":
    main()
