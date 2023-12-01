import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

report_path = os.path.join(Path(__file__).parent.parent.parent, "report/")


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
