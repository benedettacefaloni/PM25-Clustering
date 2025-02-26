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

from utils.visualize import YearlyClustering, _n_colors, plot_clustering, trace_plots

"""
Main script to plot the results of the DRPM clustering and visualize the
clustering itself.
"""

# PLOTTING -> LaTeX
use_tex = True 
if use_tex:
    plt.rc("text", usetex=True) 
    plt.rc("font", family="serif", size="16") 

colors = ["darkorange", "green", "royalblue"]


def trace_plots(res: dict, model: str, filename: str = "drpm_lower_std_trace_plots"):
    to_analyse = [ #see mh
        "mu",
        "sig2",
        "theta",
        "tau2",
        "phi0",
        "lam2",
    ]
    names = [
        "$\\mu^*_{c_1 t}$",
        "$\\sigma^{2*}_{c_1 t}$",
        "$\\theta_t$",
        "$\\tau^2_t$",
        "$\\phi_0$",
        "$\\lambda^2$",
    ]
    n_trace_plots = len(to_analyse)

    nrows = int(np.ceil(np.sqrt(n_trace_plots)))
    ncols = int(np.ceil(n_trace_plots / nrows))

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, sharex="col", figsize=(14, 9))

    for i, param_name in enumerate(to_analyse):
        row = i // ncols
        col = i % ncols

        if nrows > 1:
            ax = axes[row, col]
        else:
            ax = axes[col]

        print(param_name)
        print(res[param_name].shape)
        if res[param_name].ndim == 3:
            for week in range(3):
                ax.plot(
                    res[param_name][week, 0, :].T,
                    "--",
                    label="Week {}".format(week + 1),
                    color=colors[week],
                )
            ax.legend(loc="upper right")
        elif param_name in ["phi0", "lam2"]:
            ax.plot(res[param_name], "--", color="firebrick")
        else:
            # res[param_name].ndim == 2:
            for week in range(3):
                ax.plot(
                    res[param_name].T[week, :].T,
                    "--",
                    label="Week {}".format(week + 1),
                    color=colors[week],
                )
            ax.legend(loc="upper right")
        ax.set_ylabel("{}".format(names[i]))
        if row == 2:
            ax.set_xlabel("MCMC samples")
        # ax.set_ylabel("Y-axis")

    plt.suptitle("Trace Plots for the DRPM Model with Lower Std Prior Values")
    plt.tight_layout()
    plt.savefig("../report/imgs/drpm/{}.pdf".format(filename))
    plt.savefig("../report/imgs/drpm/{}.png".format(filename))
    plt.show()


def plot_overview(
    all_results: list[ModelPerformance],
    names: list[str],
    filename: str = "drpm_base_models_comparison",
    title: str = "",
):
    fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(14, 10), sharex=True)

    weeks = np.arange(1, 53, step=1)
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

        alpha_mean = model.test_cases[0].list_of_weekly["alpha"]
        ax[2].plot(
            weeks,
            alpha_mean,
            # label=names[idx],
            color=colors[idx],
            linestyle="--",
            marker=".",
        )

        # we use the quantile for ci = 0.05 and thus cdf(1 - 0.05/2) = cdf(0.975) = 1.96
        ci = 1.96 * model.test_cases[0].list_of_weekly["alpha_std"] / np.sqrt(52)
        ax[2].fill_between(
            weeks,
            alpha_mean - ci,
            alpha_mean + ci,
            # label=names[idx],
            color=colors[idx],
            alpha=0.1,
        )

        # cluster sizes in the third plot
        for marker_idx, cluster_kpi in enumerate(
            ["min_cluster_size", "max_cluster_size", "n_singletons"]
        ):
            ax[3].plot(
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

    # individual titles
    ax[0].set_ylabel("Mean Squared Error")
    ax[1].set_ylabel("Number of Clusters")
    ax[2].set_ylabel("$\\bar{\\alpha}_t$")
    ax[3].set_ylabel("Cluster Sizes")

    # Add the custom legend to the axis
    ax[3].legend(handles=legend_handles, loc="upper right", ncol=3)

    ax[3].set_xlabel("Week")

    lines_labels = [ax.get_legend_handles_labels() for ax in fig.axes]
    lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    ax[0].legend(lines, labels, loc="upper right", ncol=3)

    fig.align_labels()
    plt.suptitle(title)

    plt.tight_layout()
    plt.savefig("../report/imgs/drpm/{}.pdf".format(filename))
    plt.savefig("../report/imgs/drpm/{}.png".format(filename))
    plt.show()


def plot_laggedARI(
    ncols: int,
    nrows: int,
    labels: str,
    all_results: list[ModelPerformance],
    filename: str = "drpm_laggedARI",
    title: str = "",
    weeks: int = 5,
    adjusted: bool = True,
):
    if adjusted:
        key = "laggedARI"
    else:
        key = "laggedRI"

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols)

    for i, ax in enumerate(fig.axes):
        model = all_results[i]
        mat = ax.matshow(
            model.test_cases[0].list_of_weekly[key][0:weeks, 0:weeks][::-1, :],
            cmap="Blues",
            vmin=0,
            vmax=1,
        )

        ax.set_xticklabels([""] + [str(i * 10 + 1) for i in range(0, weeks)])
        ax.set_yticklabels([""] + [str(weeks - i * 10 - 1) for i in range(0, weeks)])
        ax.xaxis.tick_bottom()
        ax.tick_params(labelsize=7)

        cbar = fig.colorbar(mat, ax=ax, shrink=0.5)
        cbar.ax.tick_params(labelsize=7)

        if i == 0:
            ax.set_ylabel("Non-spatial\n \nweeks", fontdict={"size": 12})

        if i == ncols:
            ax.set_ylabel("Spatial\n\nweeks", fontdict={"size": 12})

        if i >= (nrows - 1) * ncols:
            ax.set_xlabel("weeks", fontdict={"size": 12})

        if i < ncols:
            ax.set_title(labels[i], fontsize=12)

    plt.tight_layout()
    plt.savefig("../report/imgs/drpm/{}.pdf".format(filename))
    plt.savefig("../report/imgs/drpm/{}.pdf".format(filename))


priors = {
    # params as stated in the original drpm paper of page et al.
    "paper_params": {
        # modelPriors: m0, s20, A_sigma, A_tau, A_lambda, b_e (xi)
        "modelPriors": ro.FloatVector([0, 100**2, 10, 5, 5, 1]),
        # modelPriors: a_alpha, b_alpha -> most mass on the value of 0.5
        "alphaPriors": ro.r["matrix"](ro.FloatVector([2.0, 2.0]), nrow=1),
        "SpatialCohesion": 3,
        "spatial": False,
    },
    # tuned params
    "lower_std": {
        # A_sigma is way smaller => smaller clusters in general
        # A_tau, A_lambda also smaller to set incentives for smaller clusters
        "modelPriors": ro.FloatVector([0, 100 * 2, 0.1, 1, 1, 1]),
        "alphaPriors": ro.r["matrix"](ro.FloatVector([1.0, 1.0]), nrow=1),
        "SpatialCohesion": 4,
        "spatial": False,
    },
    "mean_prev_year": {
        # A_sigma is way smaller => smaller clusters in general
        # A_tau, A_lambda also smaller to set incentives for smaller clusters
        # use the mean of log(val_2018 + 1): 2.909599862036403 as a mean prior
        "modelPriors": ro.FloatVector([2.91, 100 * 2, 0.1, 1, 1, 1]),
        # uniform prior
        "alphaPriors": ro.r["matrix"](ro.FloatVector([1.0, 1.0]), nrow=1),
        "SpatialCohesion": 4,
        "spatial": False,
    },
    "paper_params_spatial": {
        # modelPriors: m0, s20, A_sigma, A_tau, A_lambda, b_e (xi)
        "modelPriors": ro.FloatVector([0, 100**2, 10, 5, 5, 1]),
        # modelPriors: a_alpha, b_alpha -> most mass on the value of 0.5
        "alphaPriors": ro.r["matrix"](ro.FloatVector([2.0, 2.0]), nrow=1),
        "SpatialCohesion": 3,
        "spatial": True,
    },
    # tuned params
    "lower_std_spatial": {
        # A_sigma is way smaller => smaller clusters in general
        # A_tau, A_lambda also smaller to set incentives for smaller clusters
        "modelPriors": ro.FloatVector([0, 100 * 2, 0.1, 1, 1, 1]),
        "alphaPriors": ro.r["matrix"](ro.FloatVector([1.0, 1.0]), nrow=1),
        "SpatialCohesion": 4,
        "spatial": True,
    },
    "mean_prev_year_spatial": {
        # A_sigma is way smaller => smaller clusters in general
        # A_tau, A_lambda also smaller to set incentives for smaller clusters
        # use the mean of log(val_2018 + 1): 2.909599862036403 as a mean prior
        "modelPriors": ro.FloatVector([2.91, 100 * 2, 0.1, 1, 1, 1]),
        # uniform prior
        "alphaPriors": ro.r["matrix"](ro.FloatVector([1.0, 1.0]), nrow=1),
        "SpatialCohesion": 4,
        "spatial": True,
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
    for prior in [
        # "paper_params",
        "lower_std",
        # "mean_prev_year",
        # "paper_params_spatial",
        # "lower_std_spatial",
        # "mean_prev_year_spatial",
    ]:
        print(prior)
        drpm_args = {
            "M": 0.1,
            "starting_alpha": 0.5,
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
            "SpatialCohesion": priors[prior]["SpatialCohesion"],
            # cohesionPrior: mu0, k0, v0, L0
            "cParms": ro.FloatVector([0, 1, 2, 1]),
            # params for metropolis updates: sigma2, tau, lambda, eta1, phi1
            "mh": ro.FloatVector([0.5, 1, 0.1, 0.1, 0.1]),
            "verbose": False,
            "draws": 100,
            "burn": 10,
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
                data=data,
                yearly_time_series=pm25_timeseries,
                model_params=model_params,
                spatial=priors[prior]["spatial"],
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
            # trace_plots(res_cluster, model=model.name)
            model_result.add_testcase(yearly_result=yearly_result)
            it += 1
        all_results.append(model_result)

    # VISUALIZE the clustering using plotly
    # plot_clustering(save_to_visualize_cluster, method_name=model.name)

    #PLOT the MSE and cluster KPIs
    plot_overview(
        all_results=all_results,
        names=["DRPM-Paper (Page et al. 2021)", "Lower Std (ours)", "Mean 2018 (ours)"],
        # filename="drpm_spatial_informed_comparison",
        # title="Comparison of different Prior Values for the spatially informed DRPM Model",
        filename="drpm_base_models_comparison",
        title="Comparison of different Prior Values for the non-spatial informed DRPM Model",
    )

    #PRINT the ARImatrix
    for idx,model_result in enumerate(all_results):
        # plot the MSE for all three models per week
        print(idx,
              model_result.test_cases[0].list_of_weekly["partition"],
              model_result.test_cases[0].list_of_weekly["laggedRI"]
              )

    #PLOT laggedRI matrices
    plot_laggedARI(
        ncols=3,
        nrows=2,
        labels=[
            "Paper-Prior Non-spatial",
            "Lower Std Prior Non-spatial",
            "Mean 2018 Prior Non-spatial",
            "Paper-Prior spatial",
            "Lower Std Prior spatial",
            "Mean 2018 Prior spatial",
        ],
        all_results=all_results,
        filename="drpm_laggedARI",
        title="Lagged ARI for Cluster Estimates",
        weeks=52,
        adjusted=True,
    )


if __name__ == "__main__":
    main()
