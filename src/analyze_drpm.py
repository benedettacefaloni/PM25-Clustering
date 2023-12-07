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
from utils.tables import python_to_latex
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
        # "M": [0.1, 1, 10, 100, 1000],
        "M": 0.1,
        # "starting_alpha": [0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.999],
        "starting_alpha": 0,
        "unit_specific_alpha": False,
        "time_specific_alpha": False,
        # "alpha_0": [True, False],  # True to NOT update alpha
        "alpha_0": False,  # True to NOT update alpha
        # "eta1_0": [True, False],  # True for conditionally independence
        "eta1_0": False,  # True for conditionally independence
        # "phi1_0": [True, False],  # True for iid model for atoms
        "phi1_0": False,  # True for iid model for atoms
        # modelPriors: m0, s20, A_sigma, A_tau, A_lambda, b_e (xi)
        # ro.FloatVector([0, 100**2, 10, 5, 5, 1]), # -> paper values pm10
        "modelPriors": ro.FloatVector([0, 100**2, 10, 5, 5, 1]),
        # "modelPriors": ro.FloatVector([0, 100 * 2, 0.1, 1, 1, 1]),
        "alphaPriors": ro.r["matrix"](ro.FloatVector([2.0, 2.0]), nrow=1),
        "simpleModel": 0,
        "theta_tau2": ro.FloatVector([0, 2]),  # only use with simpleModel=True
        "SpatialCohesion": [3, 4],
        # cohesionPrior: mu0, k0, v0, L0
        "cParms": ro.FloatVector([0, 1, 2, 1]),
        # params for metropolis updates: sigma2, tau, lambda, eta1, phi1
        "mh": ro.FloatVector([0.5, 1, 0.1, 0.1, 0.1]),
        "verbose": False,
        "draws": 10000,
        "burn": 1000,
        "thin": 10,
    }

    model = Model("drpm", drpm_args, uses_weekly_data=False)

    all_results: list[ModelPerformance] = []

    model_result = ModelPerformance(name=model.name)

    it = 1
    for model_params in model.yield_test_cases():
        print("==========================")
        print("\nCASE {}/{}\n".format(it, model.num_experiments))
        print("==========================")
        # use yearly data
        model_args = model_params | model.load_model_specific_data(
            data=data, yearly_time_series=pm25_timeseries, model_params=model_params
        )
        res_cluster, time_needed = Cluster.cluster(model=model.name, **model_args)
        print(res_cluster.keys())
        yearly_result = YearlyPerformance(
            config=model_params,
            yearly_result_decomposed=Analyse.analyze_yearly_performance(
                py_res=res_cluster,
                target=pm25_timeseries,
                time_needed=time_needed,
                salso_args=salso_args,
            ),
        )
        # save_to_visualize_cluster = YearlyClustering(
        #     yearly_decomposed_result=yearly_result, data=data
        # )
        # plot_weekly_clustering_kpi_overview(yearly_result=yearly_result)
        # plot_clustering(save_to_visualize_cluster, method_name=model.name)
        print(yearly_result.list_of_weekly["waic"])
        print(yearly_result.list_of_weekly["lpml"])
        print(yearly_result.list_of_weekly["max_pm25_diff"])
        # trace_plots(res_cluster, model=model.name)
        model_result.add_testcase(yearly_result=yearly_result)
        it += 1

    table = model_result.to_table()
    python_to_latex(
        table,
        caption="DRPM-Model Large Experiment",
        filename="drpm_model",
        save_as_csv=True,
        cols_to_max=["lpml"],
        cols_to_min=["waic", "time", "mse", "max_pm25_diff"],
    )
    all_results.append(model_result)


if __name__ == "__main__":
    main()
