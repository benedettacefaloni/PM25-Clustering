import os
from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.robjects as ro

data_path = os.path.join(
    Path(__file__).parent.parent.parent, "data/data_aggregated.csv"
)


def load_data(year: int, week: int = None, log_scale: bool = True) -> pd.DataFrame:
    data = pd.read_csv(data_path)
    # convert time
    data["Time"] = pd.to_datetime(data["Time"])

    if log_scale:
        data["log_AQ_pm25"] = np.log(data["AQ_pm25"])
    res = data[data["Time"].dt.year == year]
    if week is not None:
        data["week_number"] = data["Time"].dt.isocalendar().week
        res = data[data["week_number"] == week]
    return res


def to_r_vector(data):
    return ro.FloatVector(data)


def to_r_matrix(data: np.ndarray):
    nrow, ncol = data.shape[0], data.shape[1]
    return ro.r["matrix"](ro.FloatVector(data), nrow=nrow, ncol=ncol)
