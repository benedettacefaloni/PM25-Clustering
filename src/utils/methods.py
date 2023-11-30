from itertools import product


class Method:
    def __init__(
        self, method: str, func_args: dict, uses_weekly_data: bool = True
    ) -> None:
        self.method = method
        # arguments for the function without the weekly
        self.func_args = func_args
        self.uses_weekly_data = uses_weekly_data

    def yield_test_cases(self, week_data):
        test_cases = self._combine_dict_lists(self.func_args)
        for test_case in test_cases:
            yield test_case.update(self._create_additional_data(week_data))

    def _combine_dict_lists(self, input_dict):
        keys = input_dict.keys()
        value_combinations = product(*(input_dict[key] for key in keys))

        result_dicts = [
            dict(zip(keys, combination)) for combination in value_combinations
        ]

        return result_dicts

    def _create_additional_data(self, data):
        # method to select which parts of the data are used as additional
        # parameters for the model
        if self.method == "sppm":
            return {"y": data["y"], "s": data["coords"]}
        elif self.method == "gaussian_ppmx":
            return {"y": data["y"], "X": data["covariates"]}
        elif self.method == "drpm":
            return {"y": data["y"], "s_coords": data["coords"]}
        else:
            raise NotImplementedError
