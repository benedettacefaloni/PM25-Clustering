import pandas as pd
import rpy2.robjects as ro

from utils import Cluster
from utils.clustering import data_path

print(data_path)
data = pd.read_csv(data_path)

data_year = data[data["year" == 2018]]
y = data_year["pm25"]
s_coords = data_year["test"]


sppm_args = {
    "y": y,
    "s": s_coords,
    "cohesion": 2,
    "M": 2,
    "modelPriors": ro.FloatVector([0, 100**2, 10, 10]),
    "cParms": ro.FloatVector([1, 1.5, 0, 1, 2, 2]),
    "mh": ro.FloatVector([0.5, 0.5]),
    "draws": 10000,
    "burn": 100,
    "thin": 10,
}
drpm_args = {
    "y": y,
    "s_coords": s_coords,
    "M": 2,
    "starting_alpha": 0.1,
    "unit_specific_alpha": False,
    "time_specific_alpha": False,
    "alpha_0": False,
    "eta1_0": False,
    "phi1_0": False,
    "modelPriors": ro.FloatVector([0, 100**2, 1, 1, 1, 1]),
    "alphaPriors": ro.r["matrix"](ro.FloatVector([1, 1]), nrow=1),
    "simpleModel": 0,
    "theta_tau2": ro.FloatVector([0, 2]),
    "SpatialCohesion": 4,
    "cParms": ro.FloatVector([0, 1, 2, 1]),
    "mh": ro.FloatVector([0.5, 1, 0.1, 0.1, 0.1]),
    "verbose": True,
    "draws": 10000,
    "burn": 100,
    "thin": 10,
}

if __name__ == "__main__":
    methods = ["sppm", "drpm"]
    methods_args = {"sppm": sppm_args, "drpm": drpm_args}

    for method in methods:
        result = Cluster.cluster(method=method, kwargs=methods_args[method])
