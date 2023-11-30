from itertools import product

from utils.data_loader import to_r_matrix, to_r_vector


class Method:
    def __init__(
        self, name: str, func_args: dict, uses_weekly_data: bool = True
    ) -> None:
        self.name = name
        # arguments for the function without the weekly
        self.func_args = func_args
        self.uses_weekly_data = uses_weekly_data

    def yield_test_cases(self):
        test_cases = self._combine_dict_lists(self.func_args)
        for test_case in test_cases:
            yield test_case

    def _combine_dict_lists(self, input_dict):
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

    def load_method_specific_data(self, data):
        # method to select which parts of the data are used as additional
        # parameters for the model
        if self.name == "sppm":
            return {
                "y": to_r_vector(data["log_pm25"]),
                "s": to_r_matrix(data[["Latitude", "Longitude"]].to_numpy()),
            }
        elif self.name == "gaussian_ppmx":
            return {
                "y": to_r_vector(data["log_pm25"]),
                # TODO: extract this --> normalize the data
                "X": data["covariates"],
            }
        elif self.name == "drpm":
            return {
                "y": to_r_vector(data["log_pm25"]),
                "s_coords": data["coords"],
            }
        else:
            raise NotImplementedError
