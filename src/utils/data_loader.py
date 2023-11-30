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


def yearly_data_as_timeseries(data):
    """
    Creates a matrix of shape (n_stations, n_timesteps) to have the full
    year as a time series, i.e. each row is the weekly pm2.5 value of ONE station
    over the entire year and each column represents the pm2.5 value of ALL stations
    for a specific week.
    """
    dict_stations = _create_time_series(data_frame=data)
    return _create_matrix_from_dict(dict_stations=dict_stations)


def _create_time_series(data_frame):
    stations = data_frame["IDStations"].unique()

    dict_stations = {}  # stations -> time series
    for station in stations:
        # Select data for current station
        data_station = data_frame[data_frame["IDStations"] == station]

        # Crea una time series per la stazione corrente
        log_pm25_series = data_station.set_index("Week")["log_pm25"]

        # Aggiungi la time series al dizionario
        dict_stations[station] = log_pm25_series

    return dict_stations


def _create_matrix_from_dict(dict_stations):
    # Obtain number of stations and max length of time series
    num_stations = len(dict_stations)
    max_length = max(len(series) for series in dict_stations.values())

    matrix = np.full((num_stations, max_length), 0)

    # Put log_pm25 values into matrix
    for idx, series in enumerate(dict_stations.values()):
        matrix[idx, : len(series)] = series.values

    return matrix
