# Autotuning

## Apr 21 Update
#### Preliminary grid search implementation done:
* Conducted numerical post-processing<br />
* Handled failed cases with timeout<br />
* Command line results are stored at `current_output.log` under the `output_0421-0` folder

## Apr 27 Update
* Revised `get_casename` in `autotune.py` to get the correct case name from `set_tests_properties` in `CTestTestfile.cmake`<br />
* Converted results to Pandas Dataframe for easier result showcase<br />
* Generated additional csv file for result access<br />
* Tried out narrower grids; results are stored under the `output_0427-X` folders<br />
* Meshgrid plots for midterm presentation -- codes/images are uploaded to folder `colormap`

## May 4 Update
* Can now run grid search with multiple samples and compute a mean of the output quantity to reduce noise.<br />

## May 5 Update
* Random Search is able to run. <br />
The `autotune.py` is now equipped with usages as follows:
```
$ python autotune.py --help
usage: autotune.py [-h] filename search

positional arguments:
  filename    YAML input filename (.yaml)
  search      searching algorithm (grid/random)
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

Upon the end of run, the resulting table would be printed to command line (and stored to csv file). For example, say the user set \#ROUNDS OF SIMULATIONS to be 2, there will be 2 identical runs for each unique case. 
```
######### TOTAL NUM OF CASES IN EACH SIMULATION: 4 #########
################### END OF SIMULATION 1 ###################

   relaxation: damping factor  relaxation: sweeps     time
0                         0.8                   1  12.7093
1                         0.9                   1  12.8434
2                         1.0                   1  12.8585
3                         1.1                   1  13.2763

```
where the resulting time above (`12.7093, 12.8434,` etc.) illustrate the **median** of all simulations of the same case (rounded to 4 digits). 

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

Upon the end of run, the resulting table would be printed to command line (and stored to csv file). For example, say the user set \#ITERS to be 2, two cases would be randomly generated as follow, 
```
######### TOTAL NUM OF CASES: 2 #########
   relaxation: damping factor  relaxation: sweeps     time
0                    0.972714                   1  12.3668
1                    1.085231                   1  12.5056
```
where the resulting time above (`12.3668, 12.5056,` etc.) illustrate the Albany Total Time for each sampled case (rounded to 4 digits). 

## \#TODO
* GPU Run<br />
* Analyses on current searching algo<br />
* Research on some advanced optimizations<br />
