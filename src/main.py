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

    sppm_args = {
        "cohesion": [1, 2],
        "M": [1e-8, 3],
        "modelPriors": ro.FloatVector([0, 100**2, 10, 10]),
        "cParms": ro.FloatVector([1, 1.5, 0, 1, 2, 2]),
        "mh": ro.FloatVector([0.5, 0.5]),
        "draws": 10000,
        "burn": 100,
        "thin": 10,
    }

    gaussian_ppmx_args = {
        "meanModel": 1,  # use additional global regression parameter
        "cohesion": 1,
        "M": 2,
        "PPM": False,  # use covariates if FALSE -> supply X
        "similarity_function": 1,
        "consim": 1,
        "calibrate": 0,
        "simParms": ro.FloatVector([0.0, 1.0, 0.1, 1.0, 2.0, 0.1, 1]),
        "modelPriors": ro.FloatVector([0, 100**2, 1, 1]),
        "mh": ro.FloatVector([0.5, 0.5]),
        "draws": 10000,
        "burn": 100,
        "thin": 10,
        "verbose": False,
    }
    drpm_args = {
        "M": 100,
        "starting_alpha": 0.75,  # 0.5
        "unit_specific_alpha": False,
        "time_specific_alpha": False,
        "alpha_0": False,
        "eta1_0": False,
        "phi1_0": False,
        # "modelPriors": ro.FloatVector([0, 100**2, 1, 1, 1, 1]),
        "modelPriors": ro.FloatVector([0, 100**2, 10, 5, 5, 1]),
        # "modelPriors": ro.FloatVector([0, 100 * 2, 0.1, 1, 1, 1]),
        "alphaPriors": ro.r["matrix"](ro.FloatVector([1, 1]), nrow=1),
        "simpleModel": 0,
        "theta_tau2": ro.FloatVector([0, 2]),
        "SpatialCohesion": 4,
        "cParms": ro.FloatVector([0, 1, 2, 1]),
        "mh": ro.FloatVector([0.5, 1, 0.1, 0.1, 0.1]),
        "verbose": False,
        "draws": 10000,
        "burn": 1000,
        "thin": 10,
    }

    num_weeks = 53
    num_weeks = 3

    model = Model("sppm", sppm_args, uses_weekly_data=True)
    # model = Model("gaussian_ppmx", gaussian_ppmx_args, uses_weekly_data=True)
    # model = Model("drpm", drpm_args, uses_weekly_data=False)

    all_results: list[ModelPerformance] = []

    model_result = ModelPerformance(name=model.name)

    for model_params in model.yield_test_cases():
        if model.uses_weekly_data:
            save_to_visualize_cluster = WeeklyClustering()

            weekly_results = []
            for week in range(1, num_weeks):
                logging.info("Week {}/{}".format(week, num_weeks))
                week_data = data[data["Week"] == week]

                week_cov_rdf = get_covariates(
                    week_data.copy().drop(columns=["Week"]),
                    as_r_df=True,
                    only_numerical=False,
                )

                model_args = model_params | model.load_model_specific_data(
                    week_data, covariates=week_cov_rdf, model_params=model_params
                )
                res_cluster, time_needed = Cluster.cluster(
                    model=model.name, **model_args
                )
                weekly_res = Analyse.analyze_weekly_performance(
                    py_res=res_cluster,
                    target=week_data["log_pm25"],
                    time_needed=time_needed,
                    salso_args=salso_args,
                    model_name=model.name,
                )

                # save the results for visualization
                save_to_visualize_cluster.add_week(
                    week_number=week, weekly_data=week_data, weekly_res=weekly_res
                )
                # plot the param distribution: trace plots and histograms
                # param_distribution(res_cluster, model.name)

                # save the results for performance evaluation
                weekly_results.append(weekly_res)

            # aggregate the performance metrics
            yearly_result = YearlyPerformance(
                config=model_params, weekly_results=weekly_results
            )

        else:
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
            print(yearly_result.list_of_weekly["waic"])
            print(yearly_result.list_of_weekly["lpml"])

        # plot_weekly_clustering_kpi_overview(
        #     yearly_result=yearly_result, num_weeks=num_weeks
        # )
        model_result.add_testcase(yearly_result=yearly_result, show_to_console=True)
    plot_clustering(save_to_visualize_cluster, method_name=model.name)
    print("Model results as table: ")
    test = model_result.to_table()
    print(test)
    # print(
    #     python_to_latex(
    #         test, cols_to_min=["time"], cols_to_max=["waic"], filename="Test"
    #     )
    # )
    all_results.append(model_result)


if __name__ == "__main__":
    main()
