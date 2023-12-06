import os
from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

data_path = os.path.join(
    Path(__file__).parent.parent.parent, "data/dataset_{}_filled.csv"
)

all_covariates = [
    "Latitude",
    "Longitude",
    "Altitude",
    "AQ_pm10",
    # "AQ_pm25", # target variable?
    # "log_pm25", # target variable?
    "AQ_co",
    "AQ_nh3",
    "AQ_nox",
    "AQ_no2",
    "AQ_so2",
    "WE_temp_2m",
    "WE_wind_speed_10m_mean",
    "WE_wind_speed_10m_max",
    "WE_mode_wind_direction_10m",
    "WE_tot_precipitation",
    "WE_precipitation_t",
    "WE_surface_pressure",
    "WE_solar_radiation",
    "WE_wind_speed_100m_mean",
    "WE_wind_speed_100m_max",
    "WE_mode_wind_direction_100m",
    "WE_blh_layer_max",
    "WE_blh_layer_min",
    "WE_rh_min",
    "WE_rh_mean",
    "WE_rh_max",
    "EM_nh3_livestock_mm",
    "EM_nh3_agr_soils",
    "EM_nh3_agr_waste_burn",
    "EM_nh3_sum",
    "EM_nox_traffic",
    "EM_nox_sum",
    "EM_so2_sum",
    "LI_pigs",
    "LI_bovine",
    "LA_hvi",
    "LA_lvi",
    "LA_land_use",
    "LA_soil_use",
]

categorical_covariates = [
    "WE_mode_wind_direction_10m",
    "WE_precipitation_t",
    "WE_mode_wind_direction_100m",
    "LA_land_use",
    "LA_soil_use",
]

ordinal_categorical_covariates = [
    "WE_precipitation_t",
    "LA_land_use",
    "LA_soil_use",
]


def get_numerical_covariates():
    return [x for x in all_covariates if x not in categorical_covariates]


def load_data(
    year: int = 2019,
    week: int = None,
) -> pd.DataFrame:
    data = pd.read_csv(data_path.format(year))
    for col in ordinal_categorical_covariates:
        data[col] = data[col].astype(str, copy=True)
    # transform non-numerical values into categorical values
    for col_name in categorical_covariates:
        data[col_name] = data[col_name].astype("category")

    # TODO: impute missing data
    # data = data.fillna(data.mode().iloc[0])  # not an appropriate solution

    # data = data.dropna(axis=0, how="any")
    data["Time"] = pd.to_datetime(data["Time"])

    if week is not None:
        return data[data["Week"] == week]
    return data


def get_covariates(
    data: pd.DataFrame,
    normalize_numerical: bool = True,
    as_r_df: bool = True,
    ignore_cols: list[str] = None,
    only_numerical: bool = False,
):
    if normalize_numerical:
        data = _normalize_numerical_attributes(data, ignore_cols=ignore_cols)
    if only_numerical:
        data = data[get_numerical_covariates()]

    if not as_r_df:
        return data
    return to_r_dataframe(data)


def _normalize_numerical_attributes(
    data: pd.DataFrame, ignore_cols: list[str] = None
) -> pd.DataFrame:
    """Mean zero and SD one for all numerical attributes"""
    data = data[all_covariates]
    numerical_covariates = get_numerical_covariates()
    data[numerical_covariates] = (
        data[numerical_covariates] - data[numerical_covariates].mean()
    ) / data[numerical_covariates].std()

    if ignore_cols is not None:
        data.drop(ignore_cols, inplace=True)
    return data


def to_r_vector(data):
    return ro.FloatVector(data)


def to_r_matrix(data: np.ndarray):
    nrow, ncol = data.shape[0], data.shape[1]
    # we need to flatten the vector and then reshape in R
    data = data.flatten()
    return ro.r["matrix"](ro.FloatVector(data), nrow=nrow, ncol=ncol)


def to_r_dataframe(
    data: pd.DataFrame,
    types_of_cols: dict[str, str] = None,
):
    """types of the form: {col_name: col_type, etc.}"""
    if types_of_cols is None:
        types_of_cols = _get_types_of_cols(data)

    # with (ro.default_converter + ro.pandas2ri.converter).context():
    #     r_df = ro.conversion.get_conversion().py2rpy(data)
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_df = ro.conversion.py2rpy(data)

    # convert the columns correctly:
    # - "factor" for categorical attributes
    # - "numeric" for floats
    for idx, name in enumerate(r_df.names):
        r_df[idx] = ro.r[types_of_cols[name]](r_df[idx])
    return r_df


def _get_types_of_cols(data: pd.DataFrame):
    """R types for each column."""
    # ignore e.g. week column
    available_cov = [col for col in list(data.columns) if col in all_covariates]
    numerical_covariates = [
        col for col in available_cov if col not in categorical_covariates
    ]
    num_cols = {col_name: "as.numeric" for col_name in numerical_covariates}
    cat_cols = {
        col_name: "factor"
        for col_name in categorical_covariates
        if col_name in available_cov
    }
    return num_cols | cat_cols


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
    """Create a matrix where each row is the pm2.5 value for a station over one year."""
    # Obtain number of stations and max length of time series
    num_stations = len(dict_stations)
    max_length = max(len(series) for series in dict_stations.values())

    matrix = np.full((num_stations, max_length), 0)

    # Put log_pm25 values into matrix
    for idx, series in enumerate(dict_stations.values()):
        matrix[idx, : len(series)] = series.values

    return matrix
