from utils.clustering import Cluster
from utils.data_loader import load_data, yearly_data_as_timeseries, get_covariates
from utils.magic import log_time, set_r_python_seed
import rpy2.robjects as ro
import logging

from utils.models import Model
from utils.results import Analyse, ModelPerformance, YearlyPerformance

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import numpy as np

from utils.visualize import (
    WeeklyClustering,
    YearlyClustering,
    _n_colors,
    plot_clustering,
    trace_plots,
)

# PLOTTING -> LaTeX
use_tex = True
if use_tex:
    plt.rc("text", usetex=True)
    plt.rc("font", family="serif", size="16")

colors = ["darkorange", "green", "royalblue"]

# Plot prestazioni del modello
def plot_overview(
    all_results: list[ModelPerformance],
    names: list[str],
    filename: str = "sspm_base_models_comparison",
    title: str = "",
):
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(14, 10), sharex=True)

    weeks = np.arange(1, 53, step=1)
    markers = ["v", "^", "o"]
    labels = ["min", "max", "n_singletons"]

    for idx, model in enumerate(all_results):
        # Plot MSE per ogni modello
        ax[0].plot(
            weeks,
            model.test_cases[0].list_of_weekly["mse"],
            label=names[idx],
            color=colors[idx],
            linestyle="--",
            marker=".",
        )

        # Plot numero di cluster per ogni settimana
        ax[1].plot(
            weeks,
            model.test_cases[0].list_of_weekly["n_clusters"],
            # label=names[idx],
            color=colors[idx],
            linestyle="--",
            marker=".",
        )

        # Plot delle dimensioni del cluster
        for marker_idx, cluster_kpi in enumerate(
            ["min_cluster_size", "max_cluster_size", "n_singletons"]
        ):
            ax[2].plot(
                weeks,
                model.test_cases[0].list_of_weekly[cluster_kpi],
                color=colors[idx],
                linestyle="--",
                marker=markers[marker_idx],
                # label=names[idx] + cluster_kpi,
            )

    # Creazione legenda personalizzata
    legend_handles = [
        Line2D(
            [0],
            [0],
            marker=marker,
            color="gray",
            # markersize=10,
            linestyle="None",
            label=label,
        )
        for marker, label in zip(markers, labels)
    ]

    # individual titles
    ax[0].set_ylabel("Mean Squared Error")
    ax[1].set_ylabel("Number of Clusters")
    ax[2].set_ylabel("Cluster Sizes")

    # Add the custom legend to the axis
    ax[2].legend(handles=legend_handles, loc="upper right", ncol=3)

    ax[2].set_xlabel("Week")

    lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    ax[0].legend(lines, labels, loc="upper right", ncol=3)

    fig.align_labels()
    plt.suptitle(title)

    plt.tight_layout()
    plt.savefig("../report/imgs/sppm/{}.pdf".format(filename))
    plt.savefig("../report/imgs/sppm/{}.png".format(filename))
    plt.show()


# modificare i parametri delle priors
priors = {
    # params as stated in the original drpm paper of page et al.
    "paper_params": {
        "modelPriors": ro.FloatVector([0, 100**2, 10, 10]),
        "M": 1e-2,
        "cohesion": 1,
    },
    # tuned params
    "mean_prev_year_var1": {
        "modelPriors": ro.FloatVector([2.9061, 1, 1, 1]),
        "M": 1e-2,
        "cohesion": 1,
    },
    "mean_prev_year_var200": {
        "modelPriors": ro.FloatVector([2.9061, 200, 1, 1]),
        "M": 1e-2,
        "cohesion": 1,
    },
}


@log_time()
def main():
    set_r_python_seed()
    data = load_data()
    pm25_timeseries = yearly_data_as_timeseries(data)
    salso_args = {"loss": "binder", "maxNCluster": 0}
    all_results: list[ModelPerformance] = []

    # for prior in priors.keys():
    for prior in ["paper_params", "mean_prev_year_var1", "mean_prev_year_var200"]:
        print(prior)
        # modificare gli argomenti in base a quelli della nostra funzione

        sppm_args = {
            "cohesion": priors[prior]["cohesion"],
            "M": priors[prior]["M"],
            "modelPriors": priors[prior]["modelPriors"],
            # parametro 1: indica la media --> può essere messo come quella dell'anno prima
            # parametro 2: deviazione std media gruppi --> bassa allora i valori delle medie dei gruppi devono essere più simili
            # parametro 3: massimo valore prior della deviazione standard di un gruppo --> bassa meno dev std nei gruppi --> più clusters
            # parametro 4: massimo valore prior della deviazione standard della media di ogni gruppo --> più è alto più la media tra diversi gruppi
            #              può essere diversa
            "cParms": ro.FloatVector([1, 1.5, 0, 1, 2, 2]),
            # parametro 1: eps della cohesion 1 (1, 2)
            # parametro 2: distance bound cohesion 2 (0.5, 1.5)
            # parametro 3: centro NNIG cohesion 3, 4
            # parametro 4: scale gaussian part NNIG cohesion 3, 4
            # parametro 5: gradi di libertà IG part di NNIG cohesion 3, 4
            # parametro 6: scale param IG part di NNIG cohesion 3, 4
            "mh": ro.FloatVector([0.5, 0.5]),
            "draws": 10000,
            "burn": 1000,
            "thin": 10,
        }

        # metto il nostro modello
        model = Model("sppm", sppm_args, uses_weekly_data=True)

        model_result = ModelPerformance(name=model.name)

        it = 1
        num_weeks = 53
        for model_params in model.yield_test_cases():
            print("==========================")
            print("\nCASE {}/{}\n".format(it, model.num_experiments))
            print("==========================")
            # use yearly data

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

            # trace_plots(res_cluster, model=model.name)
            model_result.add_testcase(yearly_result=yearly_result)
            it += 1

        all_results.append(model_result)

    # VISUALIZE the clustering using plotly
    # plot_clustering(save_to_visualize_cluster, method_name=model.name)

    print("finished")

    # PLOT the MSE and cluster KPIs
    plot_overview(
        all_results=all_results,
        names=["SPPM-Paper", "Mean 2018, Lower $\sigma_0$ (ours)", "Mean 2018, Higher $\sigma_0$ (ours)"],
        filename="sppm_spatial_informed_comparison_same_param",
        title="Comparison of different Prior Values for the SPPM Model",
    )


if __name__ == "__main__":
    main()
