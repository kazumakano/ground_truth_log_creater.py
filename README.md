# ground_truth_log_creater.py
This is Python module to interpolate ground truth position and convert logs format to CSV and pickle able to be interpreted by [particle_filter.py](https://github.com/kazumakano/particle_filter.py).

## Usage
You can run this creater as following.
You can specify config file, source file, and target directory with flags.
`config/default.yaml` will be used if unspecified.
Default target directory is `formatted/`.
```sh
python script/create_logs.py --src_file PATH_TO_SRC_FILE [--conf_file PATH_TO_CONF_FILE] [--tgt_dir PATH_TO_TGT_DIR]
```
