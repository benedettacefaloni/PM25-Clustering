import os #importing the os module in Python. The os module provides a way of interacting with the operating system, and it is commonly used for tasks such as file and directory manipulation. In my script, it's used to perform file path operations with os.path.join at line 10
from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

data_path = os.path.join( # The os.path.join function is a part of the os module in Python and is used for joining one or more path components intelligently. This function concatenates various path components into a single path using the appropriate separator for the operating system. Here's a brief explanation of how it works: It takes multiple path components as arguments. It concatenates them using the appropriate separator for the operating system (e.g., "/" for Unix-like systems and "" for Windows). It returns the joined path as a single string.
    Path(__file__).parent.parent.parent, "data/dataset_{}_filled.csv"
) #data_path is a variable used to store the path to a CSV file. is defined as the result of joining different parts of a file path using os.path.join. Path(__file__): This gets the path of the current script file (so i get where data_loader is). __file__ is a special variable in Python that represents the path of the script. Path(__file__).parent: This gets the parent directory of the script file (so i get till utils). Path(__file__).parent.parent: This gets the parent directory of the parent directory of the script file (this is the path to src). Path(__file__).parent.parent.parent: This gets the parent directory of the parent directory of the parent directory of the script file (so i get the path for PM25-Clustering-main). "data/dataset_{}_filled.csv": This is a string representing the relative path to the CSV file. The {} is a placeholder for the year variable, which will be filled in later using the format method. os.path.join(...): This function joins the path components using the appropriate separator for the operating system ("/" for Unix-based systems and "" for Windows). So, the overall result is a file path pointing to a CSV file in a directory structure relative to the location of the script. The {} placeholder in the file name allows for dynamic filling of the year variable in the path. The purpose of the variable data_path is to make it easier to refer to the location of the dataset file throughout the script. It is created using the os.path.join function to concatenate different parts of the file path. Later in the script, this data_path is used with the pd.read_csv function to read the contents of the CSV file into a Pandas DataFrame:

all_covariates = [
    "Latitude",
    "Longitude",
    "Altitude",
    "AQ_pm10",
    # "AQ_pm25", # target variable?
    # "log_pm25", # target variable?
    # "AQ_co", # dropped
    # "AQ_nh3", # dropped
    "AQ_nox",
    "AQ_no2",
    # "AQ_so2", #dropped
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
    # "LA_soil_use",  #dropped
]

categorical_covariates = [
    "WE_mode_wind_direction_10m",
    "WE_precipitation_t",
    "WE_mode_wind_direction_100m", #It appears that "WE_mode_wind_direction_10m" and "WE_mode_wind_direction_100m" represent the wind direction at different heights (10m and 100m) above the Earth's surface. The values in these columns are categorical and represent the mode (most frequent) wind direction observed during the day. This information is based on the comments you provided: "WE_mode_wind_direction_10m": Direction of the wind intensity at a height of 10m above the surface of the Earth, Daily mode, Categorical. "WE_mode_wind_direction_100m": Direction of the wind intensity at a height of 100m above the surface of the Earth, Daily mode, Categorical. In the script, these columns are identified as categorical covariates, and their data types are explicitly converted to the "category" type using the astype method. This is done to inform pandas that these columns should be treated as categorical variables, which can be beneficial for memory efficiency and certain operations.
    "LA_land_use",
    # "LA_soil_use",  #dropped
] #at line 84 I'm converting the values in these columns to the categorical data type using the astype method. This conversion is done to optimize memory usage and potentially improve performance for certain operations involving these columns.

ordinal_categorical_covariates = [ #they are numbers and i trasfrom them firstly into strings and then into the string "category" because i'm inserting them also into the categorical covariates 
    "WE_precipitation_t", #Type of precipitation on the Earth's surface, at the specified time. represents a categorical variable describing the type of precipitation on the Earth's surface at a specified time. The fact that it mentions "Daily mode" suggests that it might represent the dominant or most frequent type of precipitation on a daily basis. The conversion of this column to the string type (str) aligns with the categorical nature of the variable. Categorical variables are often represented as strings or discrete numerical values, and converting them to the string type is a common practice when dealing with categorical data in Pandas.
    "LA_land_use",
] #look at line 83: for each of these columns, the script is converting the data type of the values in those columns to strings. This conversion ensures that these columns are treated as categorical variables with an ordinal nature, even though they may have originally been stored with a different data type. The operation is performed using the astype method in Pandas, and it's specifying str as the target data type. The loop ensures that this operation is applied to each column specified in the ordinal_categorical_covariates list.


def get_numerical_covariates():
    return [x for x in all_covariates if x not in categorical_covariates]


def load_data( #i call it at line 31 of the main 
    year: int = 2019, #setting a default value for the int variable. we are considering the 2019 as year so if the year argument is not provided when calling the function, it will default to the value 2019.
    week: int = None, # if the week argument is not provided when calling the function, it will default to None. when i firstly call the funtion in the main (line 31), i do not provide any input value so i will be considering 2019 for the year and none as week  
) -> pd.DataFrame: #the expected return type for this function is a Pandas DataFrame 
    data = pd.read_csv(data_path.format(year)) #data is a Pandas Data Frame. this line reads data from a CSV file specified by the data_path and year variables and stores it in a pandas DataFrame named data. i'm considering 2019. pd.read_csv: This is a function provided by the Pandas library for reading data from CSV (Comma-Separated Values) files. data_path.format(year): This uses the format method to insert the value of the year variable into the data_path string. It's a way to dynamically generate the file path based on the specified year. So, the line is essentially loading data from a CSV file whose path is determined by the data_path and the specified year, and it creates a Pandas DataFrame named data. 
    for col in ordinal_categorical_covariates: #loop that iterates over each column specified in the ordinal_categorical_covariates list
        data[col] = data[col].astype(str, copy=True) #For each column (col) in the DataFrame data, this line converts the data type of the values in that column to a string (str). The astype method is used for this conversion. The copy=True argument ensures that a new copy of the data is created rather than modifying the original data in place. This conversion to string may be necessary if the original data types in these columns are not strings, and there's a requirement to treat them as strings, possibly for consistency or compatibility with certain operations or analyses. Yes, the astype method is a built-in method in pandas, a popular data manipulation library for Python. The astype method is used to cast a pandas object (e.g., a column of a DataFrame) to a specified dtype. he term "cast" in the context of programming, and more specifically in the context of the astype method in pandas, refers to the act of changing the data type of an object from one type to another. Here, the astype method is used to cast (or convert) the values in the specified column (data[col]) to the string (str) data type. It means that each element in the column will be transformed into its string representation. So, the line of code is essentially saying: "Take the values in the specified column and convert them to strings."
    # transform non-numerical values into categorical values
    for col_name in categorical_covariates: # to iterate over each column specified in the categorical_covariates list, and for each column, the data type of its values is changed to the categorical data type using the astype method.
        data[col_name] = data[col_name].astype("category") # This part of the loop selects the values in the current column (data[col_name]) and uses the astype method to convert them to the categorical data type. The string "category" passed as an argument specifies the target data type. In the context of pandas, the data type "category" is used to represent categorical variables. Categorical variables are variables that can take on a limited, fixed set of values

    # TODO: impute missing data
    # data = data.fillna(data.mode().iloc[0])  # not an appropriate solution

    # data = data.dropna(axis=0, how="any")
    data["Time"] = pd.to_datetime(data["Time"]) #At the column Time in the dataset I have dates like 19/04/2019. This line converts the values in the "Time" column of the DataFrame data to datetime objects using the pd.to_datetime function. This function is a part of the pandas library and is used to convert argument to datetime. In this specific case, it's transforming the values in the "Time" column to datetime objects, assuming that the values in that column represent time or date information. This conversion can be useful for various time-based operations and analyses.
    print(data["Time"])
    if week is not None: #at line 31 of the main i'm calling this function without input values so week will be equal to teh default value None 
        return data[data["Week"] == week]
    return data #i'm returning a pandas Data Frame where the categorical covariates are interpreted as "category"


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

def to_r_int_vector(data):
    return ro.IntVector(data)


def to_r_matrix(data: np.ndarray):
    nrow, ncol = data.shape[0], data.shape[1]
    # we need to flatten the vector and then reshape in R
    data = data.flatten()
    return ro.r["matrix"](ro.FloatVector(data), nrow=nrow, ncol=ncol)

def r_NULL():
    return ro.NULL

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


def yearly_data_as_timeseries(data): #I use this function in the main at line 32 after having just load the dataset into the dataframe data to create the pm25 time series. This function creates a time series matrix based on the input data which is a dataframe related to the year 2019 and wehre i'm considering the categorical covariates as "category". It first creates a dictionary (dict_stations) where each key is a station, and the corresponding value is a time series of weekly pm2.5 values for that station. Then, it uses another function _create_matrix_from_dict to convert this dictionary into a matrix. The resulting pm25_timeseries is a matrix where each row represents the weekly pm2.5 values of one station over the entire year, and each column represents the pm2.5 values of all stations for a specific week. _create_time_series(data_frame=data): This internal function creates a dictionary (dict_stations) where each key is a station, and the corresponding value is a time series of weekly pm2.5 values for that station. It extracts this information from the input DataFrame. _create_matrix_from_dict(dict_stations=dict_stations): This internal function converts the dictionary of time series into a matrix. Each row of the matrix represents the weekly pm2.5 values of one station over the entire year, and each column represents the pm2.5 values of all stations for a specific week. The resulting matrix is then returned.
    """
    Creates a matrix of shape (n_stations, n_timesteps) to have the full
    year as a time series, i.e. each row is the weekly pm2.5 value of ONE station
    over the entire year and each column represents the pm2.5 value of ALL stations
    for a specific week.
    """
    dict_stations = _create_time_series(data_frame=data)
    return _create_matrix_from_dict(dict_stations=dict_stations) # I'm transform the original DataFrame into a matrix format suitable for time series analysis, where each row represents a station, and each column represents a week with corresponding pm2.5 values.


def _create_time_series(data_frame): #stations = data_frame["IDStations"].unique(): It extracts unique station IDs from the "IDStations" column in the DataFrame. dict_stations = {}: Initializes an empty dictionary to store time series data for each station. The function then iterates over each station, selects the data for that station, and creates a time series for the "log_pm25" values indexed by the "Week" column. This time series is added to the dict_stations dictionary, where the station ID is the key. Finally, the function returns the dictionary containing time series data for each station.
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


def _create_matrix_from_dict(dict_stations): #_create_matrix_from_dict(dict_stations): This function takes the dictionary dict_stations (created by _create_time_series) as input. It determines the number of stations (num_stations) and the maximum length of time series (max_length) among all stations. Initializes a matrix (matrix) with zeros, where each row represents the pm2.5 values for a station, and each column represents a week. The function then fills the matrix with the corresponding log_pm25 values from each station's time series. The resulting matrix is returned.
    """Create a matrix where each row is the pm2.5 value for a station over one year."""
    # Obtain number of stations and max length of time series
    num_stations = len(dict_stations)
    max_length = max(len(series) for series in dict_stations.values())
    matrix = np.zeros((num_stations, max_length))

    # Put log_pm25 values into matrix
    for idx, series in enumerate(dict_stations.values()):
        matrix[idx, : len(series)] = series.values

    return matrix
