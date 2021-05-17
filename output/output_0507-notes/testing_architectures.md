## Notes on Running Sample Tests Under Different Architectures 
### CPU Build
#### k80
* Serial Build is significantly slower, so we proceed to use k80 CPU build. (May 11)
```
run_bash('ctest -L "tune-cpu" --timeout 60')
paramList['relaxation: damping factor'] = [0.5, 0.9]
simple_param_list('input_albany_Velocity_MueLu_Wedge_Tune.yaml')

chkao831@icme-gpu:~/ali-perf-tests/build/perf_tests/humboldt-3-20km$ salloc -N1 -p k80 --time=4:30:00
```
Output
```
chkao831@icme-gpu:~/ali-perf-tests/build/perf_tests/humboldt-3-20km$ python3 autotune.py 
Populated mesh already exists!
Test project /home/chkao831/ali-perf-tests/build/perf_tests/humboldt-3-20km
    Start 5: humboldt-3-20km_vel_mu_wdg_tune_np12
1/1 Test #5: humboldt-3-20km_vel_mu_wdg_tune_np12 ...   Passed   23.28 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
tune-cpu    =  23.28 sec*proc (1 test)

Total Test time (real) =  23.32 sec
Populated mesh already exists!
Test project /home/chkao831/ali-perf-tests/build/perf_tests/humboldt-3-20km
    Start 5: humboldt-3-20km_vel_mu_wdg_tune_np12
1/1 Test #5: humboldt-3-20km_vel_mu_wdg_tune_np12 ...   Passed   23.08 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
tune-cpu    =  23.08 sec*proc (1 test)

Total Test time (real) =  23.13 sec
```
#### V100
```
run_bash('ctest -L "tune-cpu" --timeout 60')
paramList['relaxation: damping factor'] = [0.5, 0.9]
simple_param_list('input_albany_Velocity_MueLu_Wedge_Tune.yaml')

chkao831@icme-gpu:~/ali-perf-tests/build/perf_tests/humboldt-3-20km$ salloc -N1 -p V100 --time=8:00:00
```
Output
```
chkao831@icme-gpu:~/ali-perf-tests/build/perf_tests/humboldt-3-20km$ python3 autotune.py 
Populated mesh already exists!
Test project /home/chkao831/ali-perf-tests/build/perf_tests/humboldt-3-20km
    Start 5: humboldt-3-20km_vel_mu_wdg_tune_np12
1/1 Test #5: humboldt-3-20km_vel_mu_wdg_tune_np12 ...   Passed   24.73 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
tune-cpu    =  24.73 sec*proc (1 test)

Total Test time (real) =  24.77 sec
Populated mesh already exists!
Test project /home/chkao831/ali-perf-tests/build/perf_tests/humboldt-3-20km
    Start 5: humboldt-3-20km_vel_mu_wdg_tune_np12
1/1 Test #5: humboldt-3-20km_vel_mu_wdg_tune_np12 ...   Passed   24.45 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
tune-cpu    =  24.45 sec*proc (1 test)

Total Test time (real) =  24.50 sec
```
### GPU build
#### k80
```
run_bash('ctest -L "tune-gpu" --timeout 200')
paramList['relaxation: damping factor'] = [0.5, 0.9]
simple_param_list('input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml')

chkao831@icme-gpu:~/ali-perf-tests/build-cuda-k80/perf_tests/humboldt-3-20km$ salloc -N1 -p k80 --gres=gpu:1 --time=4:30:00
```
Output
```
chkao831@icme-gpu:~/ali-perf-tests/build-cuda-k80/perf_tests/humboldt-3-20km$ python3 autotune.py 
Populated mesh already exists!
Test project /home/chkao831/ali-perf-tests/build-cuda-k80/perf_tests/humboldt-3-20km
    Start 3: humboldt-3-20km_vel_muk_wdg_tune_np1
1/1 Test #3: humboldt-3-20km_vel_muk_wdg_tune_np1 ...   Passed  139.42 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
tune-gpu    = 139.42 sec*proc (1 test)

Total Test time (real) = 139.47 sec
Populated mesh already exists!
Test project /home/chkao831/ali-perf-tests/build-cuda-k80/perf_tests/humboldt-3-20km
    Start 3: humboldt-3-20km_vel_muk_wdg_tune_np1
1/1 Test #3: humboldt-3-20km_vel_muk_wdg_tune_np1 ...   Passed  125.13 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
tune-gpu    = 125.13 sec*proc (1 test)

Total Test time (real) = 125.18 sec
```
#### V100
```
run_bash('ctest -L "tune-gpu" --timeout 60')
paramList['relaxation: damping factor'] = [0.5, 0.9]
simple_param_list('input_albany_Velocity_MueLuKokkos_Wedge_Tune.yaml')

chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ salloc -N1 -p V100 --gres=gpu:1 --time=8:00:00
```
Output
```
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ python3 autotune.py
Populated mesh already exists!
Test project /home/chkao831/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km
    Start 3: humboldt-3-20km_vel_muk_wdg_tune_np1
1/1 Test #3: humboldt-3-20km_vel_muk_wdg_tune_np1 ...   Passed   56.48 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
tune-gpu    =  56.48 sec*proc (1 test)

Total Test time (real) =  56.52 sec
Populated mesh already exists!
Test project /home/chkao831/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km
    Start 3: humboldt-3-20km_vel_muk_wdg_tune_np1
1/1 Test #3: humboldt-3-20km_vel_muk_wdg_tune_np1 ...   Passed   53.18 sec

100% tests passed, 0 tests failed out of 1

Label Time Summary:
tune-gpu    =  53.18 sec*proc (1 test)

Total Test time (real) =  53.23 sec
```
