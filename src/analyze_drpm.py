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
from utils.magic import log_time, set_r_python_seed
from utils.models import Model
from utils.results import Analyse, ModelPerformance, YearlyPerformance
from utils.tables import python_to_latex, _prior_values_for_caption
from utils.visualize import (
    WeeklyClustering,
    YearlyClustering,
    param_distribution,
    plot_clustering,
    plot_weekly_clustering_kpi_overview,
    trace_plots,
)

"""
Take aways:
- First experiment: using the parameters presented by page et al. -> huge Problems with too big clusters
    - nearly all stations are in the same cluster
    - best performing clusters tested for diff. combination of hyperparams
- 2nd Experiment: lowered value of sigma prior --> make cluster smaller
    - takes way longer
    - TODO: best 3 models taken for fine-tuning test

TODO:
* Further experiments:
    - use three/4 modifications for each of the three models and make a smaller table
* Plots: For one model of each category?
    - Trace plots 
    - Plot weekly errors over time (waic, mse, etc.)
    - plot cluster kpis over time
    - image of clustering for a time stamp to compare the results
"""

priors = {
    # params as stated in the original drpm paper of page et al.
    "paper_params": {
        # modelPriors: m0, s20, A_sigma, A_tau, A_lambda, b_e (xi)
        "modelPriors": ro.FloatVector([0, 100**2, 10, 5, 5, 1]),
        # modelPriors: a_alpha, b_alpha -> most mass on the value of 0.5
        "alphaPriors": ro.r["matrix"](ro.FloatVector([2.0, 2.0]), nrow=1),
    },
    # tuned params
    "smaller_std": {
        # A_sigma is way smaller => smaller clusters in general
        # A_tau, A_lambda also smaller to set incentives for smaller clusters
        "modelPriors": ro.FloatVector([0, 100 * 2, 0.1, 1, 1, 1]),
        "alphaPriors": ro.r["matrix"](ro.FloatVector([1.0, 1.0]), nrow=1),
    },
    "mean_prev_year": {
        # A_sigma is way smaller => smaller clusters in general
        # A_tau, A_lambda also smaller to set incentives for smaller clusters
        # use the mean of log(val_2018 + 1): 2.909599862036403 as a mean prior
        "modelPriors": ro.FloatVector([2.91, 100 * 2, 0.1, 1, 1, 1]),
        # uniform prior
        "alphaPriors": ro.r["matrix"](ro.FloatVector([1.0, 1.0]), nrow=1),
    },
}

experiments = {
    "large_experiment": {
        "M": [0.1, 1, 10, 100],
        "starting_alpha": [0, 0.1, 0.25, 0.5, 0.75, 0.9],
        # "alpha_0": False,
        # "eta1_0": False,
        # "phi1_0": False,
    },
    "extensions": {
        "M": 0.1,
        "starting_alpha": 0.5,
        "time_specific_alpha": [True, False],
        "eta1_0": [False, True],
        "phi1_0": [False, True],
    },
}

select_params = {
    "large_experiment": [
        "M",
        "starting_alpha",
    ],
    "extensions": [
        "M",
        "starting_alpha",
        "eta1_0",
        "phi1_0",
        "time_specific_alpha",
        "SpatialCohesion",  # --> TODO: add spatial data
    ],
}


@log_time()
def main():
    set_r_python_seed()
    data = load_data()
    pm25_timeseries = yearly_data_as_timeseries(data)
    salso_args = {"loss": "binder", "maxNCluster": 0}

    prior_case = "smaller_std"
    experiment_case = "extensions"

    drpm_args = {
        "M": experiments[experiment_case]["M"],
        "starting_alpha": experiments[experiment_case]["starting_alpha"],
        "unit_specific_alpha": False,  # diff alpha for each station --> prior needs to be adjusted
        "time_specific_alpha": experiments[experiment_case][
            "time_specific_alpha"
        ],  # diff alpha is drawn for each time-step
        "alpha_0": False,
        # True for conditionally independence
        "eta1_0": experiments[experiment_case]["eta1_0"],
        "phi1_0": experiments[experiment_case]["phi1_0"],
        "modelPriors": priors[prior_case]["modelPriors"],
        "alphaPriors": priors[prior_case]["alphaPriors"],
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

    table = model_result.to_table(select_params=select_params[experiment_case])
    python_to_latex(
        table,
        caption="DRPM Model (without spatial cohesion) for different hyperparameter configurations with the following prior values: {}.".format(
            _prior_values_for_caption(model_name="drpm", priors=priors[prior_case])
        ),
        filename="./drpm/drpm_{}_{}".format(experiment_case, prior_case),
        save_as_csv=True,
        cols_to_max=["lpml"],
        cols_to_min=["waic", "time", "mse", "max_pm25_diff"],
    )
    all_results.append(model_result)


if __name__ == "__main__":
    main()
