import csv
import os.path as path
import pickle
from datetime import datetime
from glob import iglob
from typing import Any, Union
import numpy as np
import yaml
from scipy.interpolate import interp1d


def _set_params(conf_file: str) -> None:
    global ROOT_DIR, BEGIN, FREQ

    ROOT_DIR = path.join(path.dirname(__file__), "../")

    if conf_file is None:
        conf_file = path.join(ROOT_DIR, "config/default.yaml")
    print(f"{path.basename(conf_file)} has been loaded")

    with open(conf_file) as f:
        conf: dict[str, Any] = yaml.safe_load(f)
    BEGIN = datetime.strptime(conf["begin"], "%Y-%m-%d %H:%M:%S")
    FREQ = np.float16(conf["freq"])

def _load_log(file: str) -> np.ndarray:
    data = np.loadtxt(file, dtype=np.float16, delimiter=",")
    print(f"{path.basename(file)} has been loaded")

    return data

def _resample_log(data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    resampled_ts = np.arange(data[0, 0], data[-1, 0] + 1/FREQ, step=1/FREQ, dtype=np.float64)

    resampled_pos = np.empty((len(resampled_ts), 2), dtype=np.float64)
    for i in range(2):
        resampled_pos[:, i] = interp1d(data[:, 0], data[:, i+1])(resampled_ts)

    return resampled_pos, resampled_ts

def _convert2datetime(ts: np.ndarray) -> np.ndarray:
    ts = ts.astype(object)

    offset = BEGIN - datetime.fromtimestamp(ts[0])
    for i, t in enumerate(ts):
        ts[i] = datetime.fromtimestamp(t) + offset

    return ts.astype(datetime)

def _create_log(src_file: str, tgt_dir: str) -> None:
    resampled_pos, resampled_ts = _resample_log(_load_log(src_file))
    resampled_ts = _convert2datetime(resampled_ts)

    tgt_file = path.join(tgt_dir, path.basename(src_file)[:-4] + ".csv")
    with open(tgt_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        t: datetime
        for i, t in enumerate(resampled_ts):
            writer.writerow((t.strftime("%Y-%m-%d %H:%M:%S.%f"), *resampled_pos[i]))

    print(f"written to {path.basename(tgt_file)}")

    tgt_file = path.join(tgt_dir, path.basename(src_file)[:-4] + ".pkl")
    with open(tgt_file, mode="wb") as f:
        pickle.dump((resampled_ts, resampled_pos), f)
    
    print(f"written to {path.basename(tgt_file)}")

def create_logs(src_file: Union[str, None] = None, src_dir: Union[str, None] = None, tgt_dir: Union[str, None] = None) -> None:
    if tgt_dir is None:
        tgt_dir = path.join(ROOT_DIR, "formatted/")    # save to default target directory

    if src_file is None and src_dir is None:
        for src_file in iglob(path.join(ROOT_DIR, "raw/*.csv")):    # loop for default source directory
            _create_log(src_file, tgt_dir)

    elif src_file is None:
        for src_file in iglob(src_dir):    # loop for specified source directory
            _create_log(src_file, tgt_dir)

    elif src_dir is None:
        _create_log(src_file, tgt_dir)

    else:
        raise Exception("'src_file' and 'src_dir' are specified at the same time")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf_file", help="specify config file", metavar="PATH_TO_CONF_FILE")
    parser.add_argument("--src_file", help="specify source file", metavar="PATH_TO_SRC_FILE")
    parser.add_argument("--src_dir", help="specify source directory", metavar="PATH_TO_SRC_DIR")
    parser.add_argument("--tgt_dir", help="specify target directory", metavar="PATH_TO_TGT_DIR")
    args = parser.parse_args()

    _set_params(args.conf_file)

    create_logs(args.src_file, args.src_dir, args.tgt_dir)
