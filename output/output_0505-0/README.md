Random Search

Parameters: 
```
DAMPING_FACTOR = get_truncated_normal(mean=1, sd=0.2, low=0.7, upp=1.4)
SWEEPS = list(range(1, 3))
```

Commands:
```
$ salloc -N1 -p k80 --time=4:30:00
$ python autotune.py input_albany_Velocity_MueLu_Wedge_Tune.yaml random
RANDOM SEARCH #ITERS (integer>=1): 300
RANDOM SEARCH SEED (0<=integer<=2**32): 2021
```
