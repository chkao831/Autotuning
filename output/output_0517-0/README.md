Random Search (on Multiple Smoothers)

Parameters:
```

    TYPE = ['Two-stage Gauss-Seidel', 'MT Gauss-Seidel']
    DAMPING_FACTOR_1 = get_truncated_normal(0.4, 0.2, 0.1, 0.7)
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

```
Commands:
```
$ salloc -N1 -p V100 --time=8:00:00
$ python3 autotune.py input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml random-multi
YAML INPUT FILENAME:  input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml
SEARCHING ALGORITHM:  random-multi
CASENAME: humboldt-3-20km_vel_muk_wdg_tune_np1
RANDOM SEARCH #ITERS (integer>=1): 384
RANDOM SEARCH SEED (0<=integer<=2**32): 2021
```
