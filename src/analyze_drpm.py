import logging

import pandas as pd
import rpy2.robjects as ro

from utils.clustering import Cluster
from utils.data_loader import (
    all_covariates,
    get_covariates,
    get_numerical_covariates,
    load_data,
    to_r_dataframe,
    yearly_data_as_timeseries,
)
from utils.magic import set_r_python_seed
from utils.models import Model
from utils.results import Analyse, ModelPerformance, YearlyPerformance
from utils.visualize import (
    WeeklyClustering,
    YearlyClustering,
    param_distribution,
    plot_clustering,
    plot_weekly_clustering_kpi_overview,
    trace_plots,
)


def main():
    set_r_python_seed()
    data = load_data()
    pm25_timeseries = yearly_data_as_timeseries(data)
    salso_args = {"loss": "binder", "maxNCluster": 0}

    drpm_args = {
        "M": 100,
        "starting_alpha": 0.5,  # 0.1
        "unit_specific_alpha": False,
        "time_specific_alpha": False,
        "alpha_0": False,
        "eta1_0": False,
        "phi1_0": False,
        # "modelPriors": ro.FloatVector([0, 100**2, 1, 1, 1, 1]),
        "modelPriors": ro.FloatVector([0, 100 * 2, 0.1, 1, 1, 1]),
        "alphaPriors": ro.r["matrix"](ro.FloatVector([1, 1]), nrow=1),
        "simpleModel": 0,
        "theta_tau2": ro.FloatVector([0, 2]),
        "SpatialCohesion": 4,
        "cParms": ro.FloatVector([0, 1, 2, 1]),
        "mh": ro.FloatVector([0.5, 1, 0.1, 0.1, 0.1]),
        "verbose": False,
        "draws": 10000,
        "burn": 100,
        "thin": 10,
    }

    model = Model("drpm", drpm_args, uses_weekly_data=False)

    all_results: list[ModelPerformance] = []

    model_result = ModelPerformance(name=model.name)

    for model_params in model.yield_test_cases():
        # use yearly data
        model_args = model_params | model.load_model_specific_data(
            data=data, yearly_time_series=pm25_timeseries, model_params=model_params
        )
        res_cluster, time_needed = Cluster.cluster(model=model.name, **model_args)
        yearly_result = YearlyPerformance(
            config=model_params,
            yearly_result_decomposed=Analyse.analyze_yearly_performance(
                py_res=res_cluster,
                target=pm25_timeseries,
                time_needed=time_needed,
                salso_args=salso_args,
            ),
        )
        save_to_visualize_cluster = YearlyClustering(
            yearly_decomposed_result=yearly_result, data=data
        )
        plot_weekly_clustering_kpi_overview(yearly_result=yearly_result)
        plot_clustering(save_to_visualize_cluster, method_name=model.name)
        print(yearly_result.list_of_weekly["waic"])
        print(yearly_result.list_of_weekly["lpml"])

    model_result.add_testcase(yearly_result=yearly_result)
    all_results.append(model_result)


if __name__ == "__main__":
    main()
