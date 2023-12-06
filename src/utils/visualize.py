import itertools
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly_express as px
import seaborn as sns
from tabulate import tabulate

from utils.results import YearlyPerformance, cluster_size_weekly_kpi

report_path = os.path.join(Path(__file__).parent.parent.parent, "report/")
from abc import ABC

visualize_clustering_cols = [
    "IDStations",
    "Latitude",
    "Longitude",
    "Altitude",
    "AQ_pm25",
    "Week",
    "Cluster",
]
select_from_data = [
    "IDStations",
    "Latitude",
    "Longitude",
    "Altitude",
    "AQ_pm25",
]


class VisualizeClustering(ABC):
    def get_data(self):
        raise NotImplementedError


class YearlyClustering(VisualizeClustering):
    def __init__(
        self,
        data: pd.DataFrame,
        yearly_decomposed_result: YearlyPerformance,
    ):
        weekly_partitions = yearly_decomposed_result.list_of_weekly["partition"]
        self.database = data[data["Week"] == 1][select_from_data].copy().reset_index()
        self.database["Cluster"] = pd.Series(weekly_partitions[0])
        self.database["Week"] = 1

        for week_number in range(1, len(weekly_partitions)):
            week_data_with_labels = (
                data[data["Week"] == week_number + 1][select_from_data]
                .copy()
                .reset_index()
            )
            week_data_with_labels["Cluster"] = pd.Series(weekly_partitions[week_number])
            week_data_with_labels["Week"] = week_number + 1
            self.database = pd.concat(
                [self.database, week_data_with_labels], ignore_index=True
            )

    def get_data(self):
        return self.database


class WeeklyClustering(VisualizeClustering):
    def __init__(self):
        self.database = pd.DataFrame(
            columns=visualize_clustering_cols,
            index=["IDStations"],
        )

    def add_week(
        self, week_number: int, weekly_data: pd.DataFrame, weekly_res: pd.DataFrame
    ):
        week_data_with_labels = weekly_data[select_from_data].copy().reset_index()
        week_data_with_labels["Cluster"] = pd.Series(
            weekly_res["salso_partition"]
        ).astype(str)
        week_data_with_labels["Week"] = week_number
        self.database = pd.concat(
            [self.database, week_data_with_labels], ignore_index=True
        )

    def get_data(self):
        return self.database.iloc[1:]


def plot_clustering(
    visualize_clustering: VisualizeClustering,
    method_name: str = "",
    scale_bubble_size: float = 10.0,
):
    data = visualize_clustering.get_data()

    data["AQ_pm25_scaled"] = scale_bubble_size * data["AQ_pm25"]
    n_colors = int(data["Cluster"].max())
    colors = generate_color_palette(n_colors)

    fig = px.scatter_mapbox(
        data_frame=data,
        lat="Latitude",
        lon="Longitude",
        hover_name="IDStations",
        hover_data=["AQ_pm25", "Altitude"],
        size="AQ_pm25_scaled",
        color="Cluster",
        animation_frame="Week",
        animation_group="Cluster",
        zoom=7.3,
        color_discrete_map=colors,
        title="Weekly-based clustering of PM2.5 data using {} model.".format(
            method_name
        ),
    )
    fig.update_layout(mapbox_style="open-street-map")
    # fig["layout"].pop("updatemenus") # ignore the play/pause button
    fig.show()


def generate_marker_styles_palette():
    markers = itertools.cycle(
        ["o", "s", "*", "v", "^", "D", "h", "x", "+", "8", "p", "<", ">", "d", "H"]
    )
    styles = itertools.cycle(["-", "--", "-.", ":"])
    return markers, styles


def _n_colors(n):
    return list(sns.color_palette("Set1", n_colors=n).as_hex())


def generate_color_palette(n):
    # Use the Set1 color palette from ColorBrewer
    return {str(idx + 1): str(col) for idx, col in enumerate(_n_colors(n))}


def param_distribution(res: dict, model_name: str):
    if model_name == "sppm":
        to_analyse = ["mu", "sig2", "mu0", "sig20"]
    elif model_name == "gaussian_ppmx":
        to_analyse = ["mu", "sig2", "mu0", "sig20"]
        raise NotImplementedError
    elif model_name == "drpm":
        raise NotImplementedError
    else:
        raise NotImplementedError
    n_trace_plots = len(to_analyse)

    nrows = n_trace_plots
    ncols = 2

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12, 8))

    for i, param_name in enumerate(to_analyse):
        axes[i, 0].plot(res[param_name])
        axes[i, 1].hist(res[param_name], density=True)

        # labels and plotting
        axes[i, 0].set_title("Trace Plot for {}".format(param_name))
        axes[i, 0].set_xlabel("MCMC samples")
        # axes[i, 0].set_ylabel("Trace Plot")

        axes[i, 0].set_title("Density for {}".format(param_name))
        # axes[i, 0].set_ylabel("")
        # axes[i, 0].set_ylabel("Trace Plot")

    plt.tight_layout()
    plt.suptitle("Trace plots for {} model".format(model_name))
    plt.show()


def trace_plots(res: dict, model: str):
    if model == "sppm":
        to_analyse = ["mu", "sig2", "mu0", "sig20"]
    elif model == "gaussian_ppmx":
        to_analyse = ["mu", "sig2", "mu0", "sig20"]
    elif model == "drpm":
        raise NotImplementedError
    else:
        raise NotImplementedError
    n_trace_plots = len(to_analyse)

    nrows = int(np.ceil(np.sqrt(n_trace_plots)))
    ncols = int(np.ceil(n_trace_plots / nrows))

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12, 8))

    for i, param_name in enumerate(to_analyse):
        row = i // ncols
        col = i % ncols

        if nrows > 1:
            ax = axes[row, col]
        else:
            ax = axes[col]

        ax.plot(res[param_name])
        ax.set_title("Plot {}".format(param_name))
        ax.set_ylabel("MCMC samples")
        # ax.set_ylabel("Y-axis")

    plt.tight_layout()
    plt.suptitle("Trace plots for {} model".format(model))
    plt.show()


def compare_clustering_methods(
    models_yearly: list[YearlyPerformance],
    model_names: list[str],
    num_weeks: int = 52,
) -> None:
    fig, axes = plt.subplots(nrows=2, ncols=6, figsize=(12, 8))
    weeks = np.arange(1, num_weeks + 1, step=1)

    for idx, kpi_name in enumerate(cluster_size_weekly_kpi.keys()):
        ax = axes[int(idx % 3), int(idx % 2)]
        for method_name, method in zip(model_names, models_yearly):
            ax.plot(
                weeks,
                method.list_of_weekly[kpi_name],
                label=method_name,
            )
        ax.title()
        ax.set_title("{}".format(kpi_name))
        ax.set_xlabel("Weeks")
    plt.show()


def plot_weekly_clustering_kpi_overview(
    yearly_result: YearlyPerformance, num_weeks: int = 52
) -> None:
    weeks = np.arange(1, num_weeks + 1, step=1)
    # markers, styles = generate_marker_styles_palette()
    # colors = _n_colors(len(cluster_size_weekly_kpi.keys()))

    for idx, kpi_name in enumerate(cluster_size_weekly_kpi.keys()):
        plt.plot(
            weeks,
            yearly_result.list_of_weekly[kpi_name],
            label=kpi_name,
            # color=colors[idx],
            # marker=next(markers),
            # linestyle=next(styles),
        )
    plt.xlabel("Weeks")
    plt.legend(loc="upper right")
    plt.title("Weekly Clustering")
    plt.show()


def experiment_to_table(filename: str, path: str = report_path):
    # TODO
    pass
