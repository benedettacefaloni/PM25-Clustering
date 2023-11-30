import numpy as np
import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages

from utils import Cluster
from utils.data_loader import load_data, to_r_matrix, to_r_vector
from utils.methods import Method

salso = rpackages.importr("salso")

data = load_data(year=2018, week=1, log_scale=False)
y = to_r_vector(data["AQ_pm25"])
print(data["AQ_pm25"].to_numpy().shape)

s_coords = to_r_matrix(data[["Latitude", "Longitude"]].to_numpy())

data_yearly = load_data(year=2018, log_scale=False, time_to_unix=True)

# y=(3,10) and s=(3,2)
print(
    # data_yearly[["AQ_pm25", "Unix_Time"]].to_numpy().shape
    data_yearly["AQ_pm25"]
    .to_numpy()[np.newaxis, :]
    .shape
)
print(data_yearly[["Latitude", "Longitude"]].to_numpy().shape)

# reshape: we need (n_stations, T)
y_yearly = to_r_matrix(data_yearly["AQ_pm25"].to_numpy()[:1000, np.newaxis])
s_coords_yearly = to_r_matrix(data_yearly[["Latitude", "Longitude"]].to_numpy())


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
    "y": y_yearly,
    "s_coords": s_coords_yearly,
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
    "draws": 1000,  # 10000,
    "burn": 100,
    "thin": 10,
}

if __name__ == "__main__":
    # methods = ["sppm", "drpm"]
    # methods = ["sppm"]
    methods = ["drpm"]
    methods_args = {"sppm": sppm_args, "drpm": drpm_args}

    for method in methods:
        print("Method name {}".format(method))
        r_res, py_res = Cluster.cluster(method=method, **methods_args[method])
        final_partition = salso.salso(r_res[2], loss="binder", maxNClusters=0)
        print(final_partition)
        # print(result.keys())
        # print(len(result["nclus"]))
        # print(result["WAIC"])
        # print(result["lpml"])
        # print("Method name {} FINISHED".format(method))


"""
for method in methods:
    for config in configurations:
        
        if weekly:
            for week in weeks:
                do sth.

"""


class WeeklyResult:
    pass


class MethodResult:
    def __init__(self, weekly_data: list = None, yearly_data=None):
        pass


# TODO:
# - function to create the weekly data
# - ordering is different --> use the python dict and transform it back?


class ExperimentResult:
    def __init__(self, config, yearly_result):
        pass

    def add_weekly_data():
        pass

    def yearly_aggregate():
        pass


class YearlyResult:
    def __init__(self, weekly_data: list[WeeklyResult], yearly_result):
        self.weekly = []

    def add_weekly(self, week: WeeklyResult):
        self.weekly.append(week)


[method1, Method2]
for method in methods:
    for week in weeks:
        for test in method.generate_test_cases(week):
            res = method.function(test)
            method.add_weekly(res)
    method.aggregate_yearly()
