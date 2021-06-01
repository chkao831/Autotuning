## autotune\_grid.py
### Usage:
```
$ python3 autotune_grid.py --help
usage: autotune_grid.py [-h] yaml_input_file grid_search_smoother

positional arguments:
  yaml_input_file       YAML input filename (with .yaml extension)
  grid_search_smoother  Smoother(s): (single/multiple)

optional arguments:
  -h, --help            show this help message and exit
```
**single:** on single smoother; **multiple:** on two smoothers

## autotune\_random.py
### Usage:
```
$ python3 autotune_random.py --help
usage: autotune_random.py [-h] yaml_input_file random_search_smoother

positional arguments:
  yaml_input_file       YAML input filename (with .yaml extension)
  random_search_smoother
                        Smoother(s): (single/multiple)

optional arguments:
  -h, --help            show this help message and exit
```
**single:** on single smoother; **multiple:** on two smoothers

*These two files together are **equivalent to autotune.py** at the master directory, except that grid search and random search are separated.*
