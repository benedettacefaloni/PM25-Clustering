import os
from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.robjects as ro

data_path = os.path.join(
    Path(__file__).parent.parent.parent, "data/dataset_{}_cleaned.csv"
)


def load_data(
    year: int = 2019,
    week: int = None,
) -> pd.DataFrame:
    data = pd.read_csv(data_path.format(year))
    data["Time"] = pd.to_datetime(data["Time"])

    if week is not None:
        return data[data["Week"] == week]
    return data


def to_r_vector(data):
    return ro.FloatVector(data)


def to_r_matrix(data: np.ndarray):
    nrow, ncol = data.shape[0], data.shape[1]
    # we need to flatten the vector and then reshape in R
    data = data.flatten()
    return ro.r["matrix"](ro.FloatVector(data), nrow=nrow, ncol=ncol)


def create_matrix_from_dict(dict_stations):
    """Create a matrix where each row is the pm2.5 value for a station over one year."""
    # Obtain number of stations and max length of time series
    num_stations = len(dict_stations)
    max_length = max(len(series) for series in dict_stations.values())

    # Initialize matrix with NaN values
    matrix = np.full((num_stations, max_length), np.nan)

    # Put log_pm25 values into matrix
    for idx, series in enumerate(dict_stations.values()):
        matrix[idx, : len(series)] = series.values

    return matrix
