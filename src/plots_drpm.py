from utils.clustering import Cluster
from utils.data_loader import load_data, yearly_data_as_timeseries
from utils.magic import log_time, set_r_python_seed
import rpy2.robjects as ro

from utils.models import Model
from utils.results import Analyse, ModelPerformance, YearlyPerformance

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import numpy as np

from utils.visualize import _n_colors, trace_plots

# PLOTTING -> LaTeX
use_tex = True
if use_tex:
    plt.rc("text", usetex=True)
    plt.rc("font", family="serif", size="16")


def plot_overview(
    all_results: list[ModelPerformance],
    names: list[str],
    filename: str = "drpm_base_models_comparison",
    title: str = "",
):
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(10, 12), sharex=True)

    weeks = np.arange(1, 53, step=1)
    colors = ["darkorange", "green", "royalblue"]
    markers = ["v", "^", "o"]
    labels = ["min", "max", "n_singletons"]

    for idx, model in enumerate(all_results):
        # plot the MSE for all three models per week
        ax[0].plot(
            weeks,
            model.test_cases[0].list_of_weekly["mse"],
            label=names[idx],
            color=colors[idx],
            linestyle="--",
            marker=".",
        )

        # plot the number of clusters per week
        ax[1].plot(
            weeks,
            model.test_cases[0].list_of_weekly["n_clusters"],
            # label=names[idx],
            color=colors[idx],
            linestyle="--",
            marker=".",
        )

        # cluster sizes in the third plot
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

    # Create custom legend for the last plot
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
    # Add the custom legend to the axis
    ax[2].legend(handles=legend_handles, loc="upper right", ncol=3)

    # individual titles
    ax[0].set_ylabel("Mean Squared Error")
    ax[1].set_ylabel("Number of Cluster")
    ax[2].set_ylabel("Cluster Sizes")

    ax[2].set_xlabel("Week")

    lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    ax[0].legend(lines, labels, loc="upper right", ncol=3)

    fig.align_labels()
    plt.suptitle(title)

    plt.tight_layout()
    plt.savefig("../report/imgs/{}.pdf".format(filename))
    plt.savefig("../report/imgs/{}.png".format(filename))
    plt.show()


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


@log_time()
def main():
    set_r_python_seed()
    data = load_data()
    pm25_timeseries = yearly_data_as_timeseries(data)
    salso_args = {"loss": "binder", "maxNCluster": 0}
    all_results: list[ModelPerformance] = []

    for prior in priors.keys():
        # for prior in ["paper_params"]:
        print(prior)
        drpm_args = {
            "M": 0.1,  # TODO: always the best?
            "starting_alpha": 0.25,  # TODO: always the best?
            "unit_specific_alpha": False,  # diff alpha for each station --> prior needs to be adjusted
            "time_specific_alpha": True,  # diff alpha is drawn for each time-step
            "alpha_0": False,
            # True for conditionally independence
            "eta1_0": True,
            "phi1_0": True,
            "modelPriors": priors[prior]["modelPriors"],
            "alphaPriors": priors[prior]["alphaPriors"],
            "simpleModel": 0,
            "theta_tau2": ro.FloatVector([0, 2]),  # only use with simpleModel=True
            "SpatialCohesion": 3,
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
            # trace_plots(res_cluster, model=model.name)
            model_result.add_testcase(yearly_result=yearly_result)
            it += 1
        all_results.append(model_result)

    # PLOT the MSE and cluster KPIs
    plot_overview(
        all_results=all_results,
        names=["DRPM-Paper (Page et al. 2021)", "Lower Std (ours)", "Mean 2018 (ours)"],
        title="Comparison of different Prior Values for the non-spatial DRPM Model",
    )


if __name__ == "__main__":
    main()
