Random Search

Parameters: 
```
DAMPING_FACTOR = get_truncated_normal(mean=1, sd=0.1, low=0.8, upp=1.2)
SWEEPS = list(range(1, 2))
```

Commands:
```
$ salloc -N1 -p V100 --time=8:00:00
$ python autotune.py input_albany_Velocity_MueLu_Wedge_Tune.yaml random
RANDOM SEARCH #ITERS (integer>=1): 200
RANDOM SEARCH SEED (0<=integer<=2**32): 2021
```
