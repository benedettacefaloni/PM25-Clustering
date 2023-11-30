import os
from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri

from utils.magic import log_time

drpm = rpackages.importr("drpm")
ppmSuite = rpackages.importr("ppmSuite")


# TODO:
# dataloader --> log-scale
# return object
# Analyzer: salso R-package


class Cluster:
    @staticmethod
    @log_time(get_time=False)
    def cluster(method: str, as_dict: bool = True, **kwargs):
        if method == "sppm":
            # input shapes: Y = (n_stations,) , s_coords = (n_stations, 2)
            res = ppmSuite.sppm(**kwargs)
        elif method == "ppmx":
            # input shapes: Y = (n_stations,) , s_coords = (n_stations, 2)
            res = ppmSuite.gaussian_ppmx(**kwargs)
        elif method == "drpm":
            # input shapes: Y = (n_stations, n_time_steps) time_steps have to be ordered
            # s_coords = (n_time_steps, 2) or s_coords = (n_stations, 2)
            res = drpm.drpm_fit(**kwargs)
        else:
            raise NotImplementedError("Invalid choice of method.")
        # conversion of the return types
        if as_dict:
            return convert_to_dict(res)
        else:
            return res


def salso_clustering():
    pass


def convert_to_dict(result: ro.vectors.ListVector) -> dict:
    return {name: np.array(result[idx]) for idx, name in enumerate(result.names)}
