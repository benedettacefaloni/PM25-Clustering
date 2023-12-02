import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly_express as px
import seaborn as sns
import streamlit as st
from tabulate import tabulate

report_path = os.path.join(Path(__file__).parent.parent.parent, "report/")


def plot_clustering(data_with_labels: pd.DataFrame):
    n_colors = data_with_labels["label"].max()
    colors = generate_color_palette(n_colors)
    # data_with_labels["color"] = data_with_labels["label"].apply(lambda x: colors[x - 1])
    print(data_with_labels["label"])
    data_with_labels["log_pm25"] = np.exp(data_with_labels["log_pm25"])
    data_with_labels["cluster"] = data_with_labels["label"].astype(str)

    fig = px.scatter_mapbox(
        data_frame=data_with_labels,
        lat="Latitude",
        lon="Longitude",
        hover_name="IDStations",
        hover_data="log_pm25",
        size="log_pm25",
        color="cluster",
        zoom=7.5,
        color_discrete_map=colors,
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig
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
