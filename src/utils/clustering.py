import os
from pathlib import Path

import numpy as np
import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri

drpm = rpackages.importr("drpm")
ppmSuite = rpackages.importr("ppmSuite")


# TODO:
# dataloader --> log-scale
# return object
# Analyzer: salso R-package


class Cluster:
    @staticmethod
    def cluster(method: str, as_dict: bool = True, **kwargs):
        if method == "sppm":
            res = ppmSuite.sppm(**kwargs)
        elif method == "ppmx":
            res = ppmSuite.gaussian_ppmx(**kwargs)
        elif method == "drpm":
            res = drpm.drpm_fit(**kwargs)
        else:
            raise NotImplementedError("Invalid choice of method.")
        # conversion of the return types
        if as_dict:
            return convert_to_dict(res)
        else:
            return res


def convert_to_dict(result: ro.vectors.ListVector) -> dict:
    return {name: np.array(result[idx]) for idx, name in enumerate(result.names)}
