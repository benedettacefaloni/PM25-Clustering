from itertools import product

import numpy as np
import pandas as pd

from utils.data_loader import to_r_matrix, to_r_vector


class Model:
    def __init__(
        self, name: str, func_args: dict, uses_weekly_data: bool = True
    ) -> None:
        self.name = name
        # parameters the model used
        self.func_args = func_args
        self.uses_weekly_data = uses_weekly_data

    def yield_test_cases(self):
        test_cases = self._combine_dict_lists(self.func_args)
        for test_case in test_cases:
            yield test_case

    def _combine_dict_lists(self, input_dict):
        """
        For each model with have a dict with keys, lists/single values to easily test
        multiple configurations. This model generates multiple dicts based on a dict of
        lists by applying the cartesian product of all combinations.
        """
        keys = input_dict.keys()
        # the parameters are either lists or single values
        value_combinations = product(
            *(
                input_dict[key]
                if isinstance(input_dict[key], list)
                else [input_dict[key]]
                for key in keys
            )
        )

        result_dicts = [
            dict(zip(keys, combination)) for combination in value_combinations
        ]

        return result_dicts

    def load_model_specific_data(
        self,
        data: pd.DataFrame,
        model_params: dict,
        yearly_time_series: np.ndarray = None,
        covariates: pd.DataFrame = None,
    ):
        # model to select which parts of the data are used as additional
        # parameters for the model
        if self.name == "sppm":
            return {
                "y": to_r_vector(data["log_pm25"]),
                "s": to_r_matrix(data[["Latitude", "Longitude"]].to_numpy()),
            }
        elif self.name == "gaussian_ppmx":
            param = {
                "y": to_r_vector(data["log_pm25"]),
            }
            if model_params["PPM"]:  # no covariates
                return param
            return param | {
                "X": covariates,
            }
        elif self.name == "drpm":
            return {
                "y": to_r_matrix(yearly_time_series),
                "s_coords": to_r_matrix(data[["Latitude", "Longitude"]].to_numpy()),
            }
        else:
            raise NotImplementedError


def get_fitted_attr_name(model_name: str):
    """Names for the fitted attribute given different models."""
    if model_name == "sppm":
        return "fitted"
    elif model_name == "gaussian_ppmx":
        return "fitted.values"
    else:
        raise NotImplementedError
