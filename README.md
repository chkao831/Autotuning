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

The `autotune.py` is now equipped with usages as follows:
```
$ python autotune.py --help
usage: autotune.py [-h] [-s SIMULATIONS] filename

positional arguments:
  filename              YAML input filename

optional arguments:
  -h, --help            show this help message and exit
  -s SIMULATIONS, --simulations SIMULATIONS
                        Number of sampled simulations [Default=1]
```
The `filename` argument is *required*, in yaml format.<br />
The default #simulation(s) is 1, which is an *optional* argument as illustrated above. <br />
To run multiple samples, say 3, do
```
$ python autotune.py input_albany_Velocity_MueLu_Wedge_Tune.yaml -s 3

```
Then the output would be generated as follows,
```
YAML INPUT FILENAME:  input_albany_Velocity_MueLu_Wedge_Tune.yaml
NUM OF SIMULATION(s):  3
CASENAME: humboldt-3-20km_vel_mu_wdg_tune_np12


############SIMULATION 0############
Populated mesh already exists!
...(omitted)

############SIMULATION 1############
...(omitted)

############SIMULATION 2############
...(omitted)

Total #iterations (cases): 2
   relaxation: damping factor  relaxation: sweeps     time
0                         0.8                   1  12.6317
1                         0.9                   1  13.1844
```
where the resulting time above (`12.6317, 13.1844,` etc.) illustrate the average of all 3 simulations (rounded to 4 digits). 

## \#TODO
* Random Search (Week 6)<br />
