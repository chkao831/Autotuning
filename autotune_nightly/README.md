Simulation Example:
```
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ python3 autotune_nightly.py input_albany_Velocity_MueLuKokkos_Wedge.yaml ctest-20210520.json humboldt-3-20km_vel_muk_wdg_tune_np1


[mySmoother1]  {'relaxation: inner damping factor': 1.0847, 'relaxation: sweeps': 2, 'relaxation: type': 'MT Gauss-Seidel'}
[mySmoother4]  {'relaxation: type': 'Two-stage Gauss-Seidel', 'relaxation: sweeps': 3}
   iter_id  1::relaxation: inner damping factor  1::relaxation: sweeps 1::relaxation: type     4::relaxation: type  4::relaxation: sweeps time_NOX time_AlbanyTotal passed
0        0                               1.0847                      2     MT Gauss-Seidel  Two-stage Gauss-Seidel                      3     None             None   None
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ python3 autotune_nightly.py input_albany_Velocity_MueLuKokkos_Wedge.yaml ctest-20210521.json humboldt-3-20km_vel_muk_wdg_tune_np1


[mySmoother1]  {'relaxation: inner damping factor': 1.0678, 'relaxation: sweeps': 2, 'relaxation: type': 'Two-stage Gauss-Seidel'}
[mySmoother4]  {'relaxation: type': 'MT Gauss-Seidel', 'relaxation: sweeps': 4}
   iter_id  1::relaxation: inner damping factor  1::relaxation: sweeps     1::relaxation: type     4::relaxation: type  4::relaxation: sweeps time_NOX time_AlbanyTotal passed
0        0                               1.0847                      2         MT Gauss-Seidel  Two-stage Gauss-Seidel                      3   13.609          34.4281   True
1        1                               1.0678                      2  Two-stage Gauss-Seidel         MT Gauss-Seidel                      4     None             None   None
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ python3 autotune_nightly.py input_albany_Velocity_MueLuKokkos_Wedge.yaml ctest-20210522.json humboldt-3-20km_vel_muk_wdg_tune_np1


[mySmoother1]  {'relaxation: inner damping factor': 0.91, 'relaxation: sweeps': 1, 'relaxation: type': 'MT Gauss-Seidel'}
[mySmoother4]  {'relaxation: type': 'MT Gauss-Seidel', 'relaxation: sweeps': 4}
   iter_id  1::relaxation: inner damping factor  1::relaxation: sweeps     1::relaxation: type     4::relaxation: type  4::relaxation: sweeps time_NOX time_AlbanyTotal passed
0        0                               1.0847                      2         MT Gauss-Seidel  Two-stage Gauss-Seidel                      3   13.609          34.4281   True
1        1                               1.0678                      2  Two-stage Gauss-Seidel         MT Gauss-Seidel                      4      inf              inf  False
2        2                               0.9100                      1         MT Gauss-Seidel         MT Gauss-Seidel                      4     None             None   None
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ python3 autotune_nightly.py input_albany_Velocity_MueLuKokkos_Wedge.yaml ctest-20210520.json humboldt-3-20km_vel_muk_wdg_tune_np1


[mySmoother1]  {'relaxation: inner damping factor': 1.158, 'relaxation: sweeps': 1, 'relaxation: type': 'MT Gauss-Seidel'}
[mySmoother4]  {'relaxation: type': 'MT Gauss-Seidel', 'relaxation: sweeps': 3}
   iter_id  1::relaxation: inner damping factor  1::relaxation: sweeps     1::relaxation: type     4::relaxation: type  4::relaxation: sweeps time_NOX time_AlbanyTotal passed
0        0                               1.0847                      2         MT Gauss-Seidel  Two-stage Gauss-Seidel                      3   13.609          34.4281   True
1        1                               1.0678                      2  Two-stage Gauss-Seidel         MT Gauss-Seidel                      4      inf              inf  False
2        2                               0.9100                      1         MT Gauss-Seidel         MT Gauss-Seidel                      4  13.4905          34.1335   True
3        3                               1.1580                      1         MT Gauss-Seidel         MT Gauss-Seidel                      3     None             None   None
chkao831@icme-gpu:~/ali-perf-tests/build-cuda/perf_tests/humboldt-3-20km$ diff input_albany_Velocity_MueLuKokkos_Wedge_2.yaml input_albany_Velocity_MueLuKokkos_Wedge_Best.yaml 
```
