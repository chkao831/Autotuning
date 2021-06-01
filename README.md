# Autotuning

## Apr 21 Update
#### Preliminary grid search implementation done:
* Conducted numerical post-processing<br />
* Handled failed cases with timeout<br />
* Command line results are stored at `current_output.log` under the `output/output_0421-0` folder

## Apr 27 Update
* Revised `get_casename` in `autotune.py` to get the correct case name from `set_tests_properties` in `CTestTestfile.cmake`<br />
* Converted results to Pandas Dataframe for easier result showcase<br />
* Generated additional csv file for result access<br />
* Tried out narrower grids; results are stored under the `output/output_0427-X` folders<br />
* Meshgrid plots for midterm presentation -- codes/images are uploaded to folder `colormap`

## May 4 Update
* Can now run grid search with multiple samples and compute a mean of the output quantity to reduce noise.<br />

## May 5 Update
* Random Search is able to run. <br />

### Prerequisites
```
pip install --user pandas
pip install --user ruamel.yaml
pip install --user scikit-learn
```

The `autotune.py` is now equipped with usages as follows:
```
$ python autotune.py --help
usage: autotune.py [-h] filename search

positional arguments:
  filename    YAML input filename (.yaml)
  search      Searching algorithm (grid/random)
```
The `filename` argument in yaml format is *required*.<br />
The `search` type is *required*, either `grid` or `random`.<br />

### Grid Search
```
$ python autotune.py input_albany_Velocity_MueLu_Wedge_Tune.yaml grid
```
The following messages would be printed,
```
YAML INPUT FILENAME:  input_albany_Velocity_MueLu_Wedge_Tune.yaml
SEARCHING ALGORITHM:  grid
CASENAME: humboldt-3-20km_vel_mu_wdg_tune_np12
#ROUNDS OF SIMULATIONS (integer>=1):
```
where the last line `#ROUNDS OF SIMULATIONS (integer>=1):` requires a user input that specifies the number of simulations (rounds) to be run. This could be any natural number.<br />

Upon the end of run, the resulting table (ranked, in ascending order by time) would be printed to the command line (and stored to a csv file). For example, say the user set `#ROUNDS OF SIMULATIONS` to be 2, there will be 2 identical runs for each unique case (represented by each row in the following table). 
```
######### TOTAL NUM OF CASES IN EACH SIMULATION: 4 #########
#################### END OF SIMULATION 1 ###################

   relaxation: damping factor  relaxation: sweeps     time
0                         0.8                   1  12.7093
1                         0.9                   1  12.8434
2                         1.0                   1  12.8585
3                         1.1                   1  13.2763

```
where the resulting time above (`12.7093, 12.8434,` etc.) illustrate the **median** of all simulations (in this example, of the two simulations) for the same case (rounded to 4 digits). 

### Random Search
```
$ python autotune.py input_albany_Velocity_MueLu_Wedge_Tune.yaml random
```
The following messages would be printed,
```
YAML INPUT FILENAME:  input_albany_Velocity_MueLu_Wedge_Tune.yaml
SEARCHING ALGORITHM:  random
CASENAME: humboldt-3-20km_vel_mu_wdg_tune_np12
RANDOM SEARCH #ITERS (integer>=1):
```
where the last line `RANDOM SEARCH #ITERS (integer>=1):` requires a user input that specifies the number of cases to be randomly generated and run. This could be any natural number.<br />

Then, the user needs to enter another value to specify the random seed for this experiment. This integer should fall between 0 and 2^32, inclusive. 
```
RANDOM SEARCH SEED (0<=integer<=2**32):
```

Upon the end of run, the resulting table  (ranked, in ascending order by time) would be printed to the command line (and stored to a csv file). For example, say the user set `#ITERS` to be 2, two cases would be randomly generated as follows, 
```
################### TOTAL NUM OF CASES: 2 ##################
   relaxation: damping factor  relaxation: sweeps     time
0                    0.972714                   1  12.3668
1                    1.085231                   1  12.5056
```
where the resulting time above (`12.3668, 12.5056,` etc.) illustrate the Albany Total Time for each sampled case (rounded to 4 digits). 

## May 7 Update
* GPU Build completed -- [Notes on Running Sample Tests Under Different Architectures](https://github.com/chkao831/Autotuning/blob/main/output/output_0507-notes/testing_architectures.md)<br />

## May 16-17 Update
* Handled wrong command line input arguments with exceptions.<br />
### Multi-Smoother Grid Search
* Multi-Smoother Grid Search Done ([autotune.py](https://github.com/chkao831/Autotuning/blob/main/autotune.py))<br />
  * [Sample outputs](https://github.com/chkao831/Autotuning/tree/main/output/output_0516-0)<br />
  * Experiments are run on V100 GPU<br />
  * Performances are recorded by `NOX Total Linear Solve + NOX Total Preconditioner Construction`<br />
### Multi-Smoother Random Search
* Multi-Smoother Random Search Done ([autotune.py](https://github.com/chkao831/Autotuning/blob/main/autotune.py))<br />
  * [Sample outputs](https://github.com/chkao831/Autotuning/tree/main/output/output_0517-0)<br />
  * Experiments are run on V100 GPU<br />
  * Performances are recorded by `NOX Total Linear Solve + NOX Total Preconditioner Construction`<br />
 
* Now available options become `grid-single`, `grid-multi`, `random-single` and `random-multi`, respectively indicate single-smoother grid search, multi-smoother grid search, single-smoother random search and multi-smoother random search. <br />

* For example, with the choice of `grid-multi` option, 
```
$ python autotune.py input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml grid-multi

YAML INPUT FILENAME:  input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml
SEARCHING ALGORITHM:  grid-multi
CASENAME: humboldt-3-20km_vel_muk_wdg_tune_np1
#ROUNDS OF SIMULATIONS (integer>=1): 1


####################### SIMULATION 0 #######################


########################## CASE 0 ##########################
[mySmoother1]  {'relaxation: inner damping factor': 0.25, 'relaxation: sweeps': 1, 'relaxation: type': 'Two-stage Gauss-Seidel'}
[mySmoother3]  {'relaxation: damping factor': 0.8, 'relaxation: sweeps': 1, 'relaxation: type': 'Two-stage Gauss-Seidel'}
[mySmoother4]  {'relaxation: sweeps': 2, 'relaxation: type': 'Two-stage Gauss-Seidel'}
Populated mesh already exists!
Test project /home/chkao831/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km
    Start 3: humboldt-3-20km_vel_muk_wdg_tune_np1
1/1 Test #3: humboldt-3-20km_vel_muk_wdg_tune_np1 ...   Passed   48.87 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
tune-gpu    =  48.87 sec*proc (1 test)

Total Test time (real) =  48.91 sec
```
* With the choice of `random-multi` option, 
```
$ python autotune.py input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml random-multi
YAML INPUT FILENAME:  input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml
SEARCHING ALGORITHM:  random-multi
CASENAME: humboldt-3-20km_vel_muk_wdg_tune_np1
RANDOM SEARCH #ITERS (integer>=1): 384
RANDOM SEARCH SEED (0<=integer<=2**32): 2021


########################## CASE 0 ##########################
[mySmoother1]  {'relaxation: inner damping factor': 0.4464, 'relaxation: sweeps': 2, 'relaxation: type': 'Two-stage Gauss-Seidel'}
[mySmoother3]  {'relaxation: damping factor': 0.9849, 'relaxation: sweeps': 2, 'relaxation: type': 'Two-stage Gauss-Seidel'}
[mySmoother4]  {'relaxation: sweeps': 2, 'relaxation: type': 'Two-stage Gauss-Seidel'}
Populated mesh already exists!
Test project /home/chkao831/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km
    Start 3: humboldt-3-20km_vel_muk_wdg_tune_np1
1/1 Test #3: humboldt-3-20km_vel_muk_wdg_tune_np1 ...   Passed   49.00 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
tune-gpu    =  49.00 sec*proc (1 test)

Total Test time (real) =  49.05 sec

```
## Week 9 Update
* Incorporated random search to real-time data at `autotune_nightly.py`<br />
* To increase code readability, `autotune.py` is now separated into two files: `autotune_grid.py` and `autotune_random.py` without major changes in functionality.

## \#TODO
* Analyze current searching algo's for final presentation and report.<br />


