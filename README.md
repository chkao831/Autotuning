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

## \#TODO
* Random Search (Week 6)<br />
