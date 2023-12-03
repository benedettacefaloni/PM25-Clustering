import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly_express as px
import seaborn as sns
from tabulate import tabulate

report_path = os.path.join(Path(__file__).parent.parent.parent, "report/")
from abc import ABC


class VisualizeClustering(ABC):
    def get_data(self):
        raise NotImplementedError


class YearlyClustering(VisualizeClustering):
    def __init__(self, yearly_result):
        # TODO: transform
        pass

    def get_data(self):
        # TODO: get result
        pass


class WeeklyClustering(VisualizeClustering):
    def __init__(self):
        self.database = pd.DataFrame(
            columns=[
                "IDStations",
                "Latitude",
                "Longitude",
                "AQ_pm25",
                "week",
                "cluster",
            ],
            index=["IDStations"],
        )

    def add_week(
        self, week_number: int, weekly_data: pd.DataFrame, weekly_res: pd.DataFrame
    ):
        week_data_with_labels = (
            weekly_data[["IDStations", "Latitude", "Longitude", "AQ_pm25"]]
            .copy()
            .reset_index()
        )
        week_data_with_labels["cluster"] = pd.Series(
            weekly_res["salso_partition"]
        ).astype(str)
        week_data_with_labels["week"] = week_number
        self.database = pd.concat(
            [self.database, week_data_with_labels], ignore_index=True
        )

    def get_data(self):
        return self.database.iloc[1:]


def plot_clustering(weekly_clustering: WeeklyClustering, method_name: str = ""):
    data = weekly_clustering.get_data()

    n_colors = int(data["cluster"].max())
    colors = generate_color_palette(n_colors)

    fig = px.scatter_mapbox(
        data_frame=data,
        lat="Latitude",
        lon="Longitude",
        hover_name="IDStations",
        hover_data="AQ_pm25",
        size="AQ_pm25",
        color="cluster",
        animation_frame="week",
        animation_group="cluster",
        zoom=7.3,
        color_discrete_map=colors,
        title="Weekly-based clustering of PM2.5 data using {} model.".format(
            method_name
        ),
    )
    fig.update_layout(mapbox_style="open-street-map")
    # fig["layout"].pop("updatemenus") # ignore the play/pause button
    fig.show()


def generate_color_palette(n):
    # Use the Set1 color palette from ColorBrewer
    return {
        str(idx + 1): str(col)
        for idx, col in enumerate(sns.color_palette("Set1", n_colors=n).as_hex())
    }


def trace_plots(res: dict, model: str):
    if model == "sppm":
        to_analyse = ["mu", "sig2", "mu0", "sig20"]
    elif model == "gaussian_ppmx":
        raise NotImplementedError
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


def experiment_to_table(filename: str, path: str = report_path):
    pass
