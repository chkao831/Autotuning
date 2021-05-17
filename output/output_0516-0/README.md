Grid Search (on Multiple Smoothers)

Parameters:
```
TYPE = ['Two-stage Gauss-Seidel', 'MT Gauss-Seidel']
DAMPING_FACTOR_1 = [0.25, 0.5, 0.75]
SWEEP_1 = [1,2]
DAMPING_FACTOR_3 = [0.8, 1.0]
SWEEP_3 = [1,2]
SWEEP_4 = [2,4]

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
```
Commands:
```
$ salloc -N1 -p V100 --time=8:00:00
$ python3 autotune.py input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml grid-multi
#ROUNDS OF SIMULATIONS (integer>=1): 1
```
