from itertools import product

import numpy as np
import pandas as pd

# from utils.data_loader import to_r_matrix, to_r_vector
from utils.data_loader import to_r_matrix, to_r_vector, r_NULL


class Model:
    def __init__(
        self, name: str, func_args: dict, uses_weekly_data: bool = True #we always use weekly data apart from the drpm model
    ) -> None:
        self.name = name
        # parameters the model used
        self.func_args = func_args
        self.uses_weekly_data = uses_weekly_data
    #I'm calling the function yeld_test_cases at line 96 of the main fucntion for the model created with the gaussian_ppmx specifications
    def yield_test_cases(self): #i'm calling it for the model that has name = gaussian_ppmx, func_args = gaussian_ppmx_args and uses_weekly_data equal to True 
        test_cases = self._combine_dict_lists(self.func_args) #I'm calling the function combine_dict_lists where input_dict is the dictionary gaussian_ppmx_args (which contains like "meanModel": 1, "cohesion": 1 and so on). test cases will be a list of dictionaries where the keys are the gaussian_ppmx_args and the values are all the combinations for the values inside (useless for this case bc we didn't define values as lists of values)
        self.num_experiments = len(test_cases) #test_cases is a list of dictionaries, each representing a unique combinations for the parameter (but every dictionary contains all the keys of course). num_experiments is the length of that lists so it corresponds to the number of simulations we are doing (for gaussian_ppmx i'm actually doing one simulation at a time so it has to be 1)
        for test_case in test_cases: #test cases is a list of dictoonaries (the one returned by combine_dict_list) so now i'm iterating over teh elements of that list 
            yield test_case #the single test_case returned each time is just a dictionary

    def _combine_dict_lists(self, input_dict): #input_dict is the dictionary gaussian_ppmx_args *which contains like "meanModel": 1, "cohesion": 1 and so on
        """
        For each model with have a dict with keys, lists/single values to easily test
        multiple configurations. This model generates multiple dicts based on a dict of
        lists by applying the cartesian product of all combinations.
        """
        keys = input_dict.keys() #input_dict are the func_args (gaussian_ppm_args in the case i'm running so like the keys are: "meanModel", "cohesion",...)
        # the parameters are either lists or single values
        value_combinations = product( #The product function from the itertools module computes the Cartesian product of input iterables, generating all possible combinations. The syntax for the product function is as follows:itertools.product(*iterables, repeat=1) iterables: This is one or more input iterables (lists, tuples, or other iterable objects). These represent the sets of values for which you want to compute the Cartesian product. repeat: An optional parameter that specifies the number of repetitions for each element. The default is 1. In the specific context of the _combine_dict_lists method you provided, the product function is used to combine values associated with each key in the input dictionary (input_dict)
            *( #The * operator is used for argument unpacking. It unpacks the iterables (lists or single values) obtained in the previous step, providing them as separate arguments to the product function.
                input_dict[key]
                if isinstance(input_dict[key], list) # generator expression that, for each key, checks if the associated value is a list. If it is, it uses the list; otherwise, it wraps the single value in a list. This ensures that each key is associated with an iterable.
                else [input_dict[key]]
                for key in keys
            )
        ) #The product function then computes the Cartesian product of these iterables, generating all possible combinations of values. In summary, value_combinations is an iterable that yields tuples, where each tuple represents a combination of values for the parameters defined by the keys in the input dictionary. The itertools.product function returns an iterator that produces tuples containing all possible combinations of the elements from the input iterables. It does not generate a list directly but rather produces the tuples on-the-fly as you iterate over the iterator.

        result_dicts = [
            dict(zip(keys, combination)) for combination in value_combinations #value_combinations is an iterator generated by itertools.product. Each item in this iterator is a tuple representing a combination of values from the input iterables. zip(keys, combination) pairs each key from the keys iterable with its corresponding value from the current combination tuple. The zip function in Python is used to combine two or more iterables (lists, tuples, etc.) element-wise. It takes multiple iterables as arguments and returns an iterator that generates tuples containing elements from the input iterables, where the i-th tuple contains the i-th element from each of the input iterables. The dict(...) construct in Python is used to create a dictionary from an iterable of key-value pairs. It can take various forms, but in the provided context, it's used with zip to create a dictionary where keys come from one iterable (keys) and values from another iterable (combination).
        ] #result_dicts = [dict(zip(keys, combination)) for combination in value_combinations]: Creates a list of dictionaries, where each dictionary represents a combination of values. The zip(keys, combination) pairs each key with its corresponding value in the combination.

        return result_dicts #The method returns a list of dictionaries (result_dicts), where each dictionary represents a unique combination of values for the parameters. The combination is obtained by taking the Cartesian product of the values associated with each key. this doesn't make a difference for gaussian_ppmx model because in gaussian_ppmx i do not have keys associated to values which are lists 

    def load_model_specific_data(
        self,
        data: pd.DataFrame,
        model_params: dict,
        yearly_time_series: np.ndarray = None,
        covariates: pd.DataFrame = None,
        spatial: bool = True,
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
            if spatial:
                return{
                    "y": to_r_matrix(yearly_time_series),
                    "s_coords": to_r_matrix(data[["Latitude", "Longitude"]].to_numpy())
                }
            else:
                return{
                    "y": to_r_matrix(yearly_time_series),
                    "s_coords": r_NULL()
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
