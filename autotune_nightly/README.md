### Usage:
```
$ python3 autotune_nightly.py --help
usage: autotune_nightly.py [-h] yaml_input_file ctest_output_file casename

positional arguments:
  yaml_input_file    YAML input filename (w/.yaml extension)
  ctest_output_file  ctest output filename (w/.json extension)
  casename           casename
```
For example, `$ python3 autotune_nightly.py input_albany_Velocity_MueLuKokkos_Wedge.yaml ctest-20210520.json humboldt-3-20km_vel_muk_wdg_tune_np1` <br />
The 1st argument `autotune_nightly.py` is the script name. <br />
The 2nd argument `input_albany_Velocity_MueLuKokkos_Wedge.yaml` is the input yaml filename. <br />
The 3rd argument `ctest-20210520.json` specifies the previously-generated output file from which the timers are extracted. <br />
The 4th argument `humboldt-3-20km_vel_muk_wdg_tune_np1` specifies the case to be evaluated. <br />

#### Note:
* If the casename (4th argv) cannot be found from the json output file (3rd argv), a `ValueError: The casename is not found in the ctest output file` would be generated. 
* For the first run (iteration 0), where the [casename]\_hist.csv file is not yet generated, the 3rd and 4th argument would be useless, since there's no output yet. 
* The parameter constraints for random search are specified in `_properties.json` file in the same directory. 
* If `_properties.json` could not be opened, an IOError would be thrown. 

### Simulation Example:
#### Iteration: 0
```
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ python3 autotune_nightly.py input_albany_Velocity_MueLuKokkos_Wedge.yaml ctest-20210520.json humboldt-3-20km_vel_muk_wdg_tune_np1

   iter_id  1::relaxation: inner damping factor  1::relaxation: sweeps 1::relaxation: type     4::relaxation: type  4::relaxation: sweeps time_NOX time_AlbanyTotal passed
0        0                               1.0847                      2     MT Gauss-Seidel  Two-stage Gauss-Seidel                      3     None             None   None

```
By the end of the first iteration, a history file `[casename]_hist.csv` is created and the above information is written to file. Meanwhile, the input file `input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml` is updated, along with a copy of it, called `input_albany_Velocity_MueLuKokkos_Wedge_Tune_0.yaml`. 
#### Iteration: 1
Then, for the next-day iteration, given that the history file preexists, an output ctest json file should have been generated based on the previously-updated input file. 
```
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ python3 autotune_nightly.py input_albany_Velocity_MueLuKokkos_Wedge.yaml ctest-20210521.json humboldt-3-20km_vel_muk_wdg_tune_np1

   iter_id  1::relaxation: inner damping factor  1::relaxation: sweeps     1::relaxation: type     4::relaxation: type  4::relaxation: sweeps time_NOX time_AlbanyTotal passed
0        0                               1.0847                      2         MT Gauss-Seidel  Two-stage Gauss-Seidel                      3   13.609          34.4281   True
1        1                               1.0678                      2  Two-stage Gauss-Seidel         MT Gauss-Seidel                      4     None             None   None
```
Here, the timer data for iteration 0 of case `humboldt-3-20km_vel_muk_wdg_tune_np1` is extracted from `ctest-20210521.json`. Similarly, the input file `input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml` is updated, along with a copy of it, called `input_albany_Velocity_MueLuKokkos_Wedge_Tune_1.yaml`.
#### Iteration: 2
Then, for iteration 2, repeat with the new ctest json file,
```
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ python3 autotune_nightly.py input_albany_Velocity_MueLuKokkos_Wedge.yaml ctest-20210522.json humboldt-3-20km_vel_muk_wdg_tune_np1

   iter_id  1::relaxation: inner damping factor  1::relaxation: sweeps     1::relaxation: type     4::relaxation: type  4::relaxation: sweeps time_NOX time_AlbanyTotal passed
0        0                               1.0847                      2         MT Gauss-Seidel  Two-stage Gauss-Seidel                      3   13.609          34.4281   True
1        1                               1.0678                      2  Two-stage Gauss-Seidel         MT Gauss-Seidel                      4      inf              inf  False
2        2                               0.9100                      1         MT Gauss-Seidel         MT Gauss-Seidel                      4     None             None   None

```
Here, the timer data is supposedly extracted from `ctest-20210522.json`; however, the test fails, yielding the `inf` results and a boolean of `False` above.
#### Iteration: 3
Lastly, for iteration 3, repeat again, 
```
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ python3 autotune_nightly.py input_albany_Velocity_MueLuKokkos_Wedge.yaml ctest-20210520.json humboldt-3-20km_vel_muk_wdg_tune_np1

   iter_id  1::relaxation: inner damping factor  1::relaxation: sweeps     1::relaxation: type     4::relaxation: type  4::relaxation: sweeps time_NOX time_AlbanyTotal passed
0        0                               1.0847                      2         MT Gauss-Seidel  Two-stage Gauss-Seidel                      3   13.609          34.4281   True
1        1                               1.0678                      2  Two-stage Gauss-Seidel         MT Gauss-Seidel                      4      inf              inf  False
2        2                               0.9100                      1         MT Gauss-Seidel         MT Gauss-Seidel                      4  13.4905          34.1335   True
3        3                               1.1580                      1         MT Gauss-Seidel         MT Gauss-Seidel                      3     None             None   None
```

From the results, we could see that the experiment with `iter_id` = 2 gives the best result (of time_NOX). It is verified by
```
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ diff input_albany_Velocity_MueLuKokkos_Wedge_2.yaml input_albany_Velocity_MueLuKokkos_Wedge_Best.yaml 
```

*All relevant files are uploaded to the folder `autotune_nightly`.*
