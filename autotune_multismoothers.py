# Import libraries
import os
import subprocess
from sklearn.model_selection import ParameterGrid

###################################################################################################
# From Albany/tools - yaml read/write
# Need: pip install --user ruamel.yaml
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

###################################################################################################
def simple_param_list(inFile):
    '''
    Run multiple sims with a parameter list
    '''
    # Read input file
    inputDict = read_yaml(inFile)

    # Extract MueLu dictionary
    linsolDict = inputDict['ANONYMOUS']['Piro']['NOX']['Direction']['Newton']['Stratimikos Linear Solver']
    muDict = linsolDict['Stratimikos']['Preconditioner Types']['MueLu']

    # Parameter to change
    paramList_1 = muDict['Factories']['mySmoother1']['ParameterList']
    paramList_3 = muDict['Factories']['mySmoother3']['ParameterList']
    DAMPING_FACTOR = [0.75, 0.95]
    
    param_grid_1 = {'relaxation: damping factor': DAMPING_FACTOR}
    param_grid_3 = {'relaxation: damping factor': DAMPING_FACTOR}
    grid_1 = ParameterGrid(param_grid_1)
    grid_3 = ParameterGrid(param_grid_3)

    ite = 0
    for p1 in grid_1:
        dic1 = { key:((float)(round(value, 4)) if isinstance(value, float) else value) for key, value in p1.items() }
        print("P1~", dic1)
        paramList_1.update(dic1)
        for p3 in grid_3:
            dic3 = { key:((float)(round(value, 4)) if isinstance(value, float) else value) for key, value in p3.items() }
            print("P3~", dic3)
            paramList_3.update(dic3)
            write_yaml(inputDict, inFile)
            run_sim(ite, inFile)
            ite = ite + 1
    print("TOTAL ITE: ", ite)
    run_bash('python ctest2json.py')

###################################################################################################
if __name__ == "__main__":
    '''
    Run example
    '''
    simple_param_list('input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml')
