import os
from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri

from utils.magic import log_time
from utils.results import Analyse, YearlyResults

drpm = rpackages.importr("drpm")
ppmSuite = rpackages.importr("ppmSuite")


def yearly_evaluation(
    model,
    test_case,
    data: pd.DataFrame,
    pm25_timeseries: np.ndarray,
    num_weeks: int,
    salso_args={"loss": "binder", "maxNCluster": 0},
):
    if model.uses_weekly_data:
        weekly_results = []
        for week in range(1, num_weeks):
            week_data = data[data["Week"] == week]

            model_args = test_case | model.load_model_specific_data(week_data)
            res_cluster, time_needed = Cluster.cluster(model=model.name, **model_args)
            weekly_results.append(
                Analyse.analyze_weekly_result(
                    py_res=res_cluster,
                    target=week_data["log_pm25"],
                    time_needed=time_needed,
                    salso_args=salso_args,
                )
            )
        yearly_result = YearlyResults(config=test_case, weekly_results=weekly_results)

    else:
        # use yearly data
        model_args = test_case | model.load_model_specific_data(
            data=data, yearly_time_series=pm25_timeseries
        )
        res_cluster, time_needed = Cluster.cluster(model=model.name, **model_args)
        yearly_result = YearlyResults(
            config=test_case,
            yearly_result=Analyse.analyze_yearly_result(
                py_res=res_cluster,
                target=pm25_timeseries,
                time_needed=time_needed,
                salso_args=salso_args,
            ),
        )
    return yearly_result


class Cluster:
    @staticmethod
    @log_time(get_time=True)
    def cluster(model: str, as_dict: bool = True, **kwargs):
        if model == "sppm":
            # input shapes: Y = (n_stations,) , s_coords = (n_stations, 2)
            res = ppmSuite.sppm(**kwargs)
        elif model == "gaussian_ppmx":
            # input shapes: Y = (n_stations,) , s_coords = (n_stations, 2)
            res = ppmSuite.gaussian_ppmx(**kwargs)
        elif model == "drpm":
            # input shapes: Y = (n_stations, n_time_steps) time_steps have to be ordered
            # s_coords = (n_time_steps, 2) or s_coords = (n_stations, 2)
            res = drpm.drpm_fit(**kwargs)
        else:
            raise NotImplementedError("Invalid choice of model.")
        # conversion of the return types
        if as_dict:
            return convert_to_dict(res)
        return res


def convert_to_dict(result: ro.vectors.ListVector) -> dict:
    return {name: np.array(result[idx]) for idx, name in enumerate(result.names)}
