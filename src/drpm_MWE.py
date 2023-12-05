import numpy as np
import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri

from utils import Cluster
from utils.clustering import convert_to_dict
from utils.data_loader import to_r_matrix
from utils.magic import set_r_python_seed

# Activate automatic conversion of pandas objects to R objects
# pandas2ri.activate()

# Import the drpm package
drpm = rpackages.importr("drpm")
salso = rpackages.importr("salso")

import numpy as np

set_r_python_seed()
# # Set the seed for reproducibility
# np.random.seed(123)
# r = ro.r
# set_seed = r("set.seed")
# set_seed(123)

# Number of observations
nobs = 10
nstations = 4

y = (
    np.array(
        [
            2.875775,
            9.404673,
            5.514350,
            6.775706,
            2.4608773,
            8.895393,
            6.557058,
            2.891597,
            6.9070528,
            7.584595,
            7.883051,
            0.455565,
            4.566147,
            5.726334,
            0.4205953,
            6.928034,
            7.085305,
            1.471136,
            7.9546742,
            2.164079,
            4.089769,
            5.281055,
            9.568333,
            1.029247,
            3.2792072,
            6.405068,
            5.440660,
            9.630242,
            0.2461368,
            3.181810,
            8.830174,
            8.924190,
            4.533342,
            8.998250,
            9.5450365,
            9.942698,
            5.941420,
            9.022990,
            4.7779597,
            2.316258,
        ]
    )
    .reshape(nstations, nobs)
    .T
)


s = (
    np.array(
        [
            8.568001,
            9.146685,
            24.872780,
            8.328364,
            24.823460,
            13.982046,
            22.130727,
            27.957747,
        ]
    )
    .reshape((nstations, 2))
    .T
)

# Create a matrix from y_test
# y_test = np.random.uniform(0, 10, size=(nstations, nobs))
# print(y_test)

# # Spatial coordinates (s1, s2)
# s = np.random.uniform(0, 60, size=(nstations, 2))
# print(s)


# Simplify the call to the drpm_fit function
drpm_fit = drpm.drpm_fit


# print("y_test.shape = ", y_test.shape)
# print(y_test.shape)

v = ro.FloatVector(y.flatten())
m = ro.r["matrix"](v, nrow=nstations)
print("m = ")
print(type(m))
print(m)

# Spatial coordinates (s1, s2)
# s = np.random.uniform(0, 10, (n_stations, 2))
print("s.shape = ", s.shape)
s_float = ro.FloatVector(s.flatten())
s_coords = ro.r["matrix"](s_float, ncol=2)
print(s_coords)

r_data_test = {
    "y": m,
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

# py_res, time_needed = Cluster.cluster(model="drpm", as_dict=True, **r_data_test)
py_res = convert_to_dict(drpm.drpm_fit(**r_data_test))

salso_args: dict = {"loss": "binder", "maxNCluster": 0}
salso_partion = np.array(
    [
        salso.salso(
            to_r_matrix(py_res["Si"][time_step, :, :].T),
            **salso_args,
        )
        for time_step in range(nobs)
    ]
)
# print(salso_partion)
print(py_res.keys())
print(py_res["Si"])
print(py_res["fitted"])
print("Evaluation: lplm = {}, waic = {}".format(py_res["lpml"], py_res["waic"]))
print(np.min(py_res["Si"]))
print(np.max(py_res["Si"]))
print("worked")
print(salso_partion)
# Call the simplified drpm_fit function
# result = drpm_fit(**r_data_test)
"""Object attributes are
- "Si"
- "gamma"
- "mu"
- "sig2"
- "alpha"
- "theta"            
- "tau2"
- "eta1"
- "phi0"     
- "phi1" 
- "lam2"
- "llike"            
- "fitted"
- "lpml" 
- "waic"             
- "initial_partition"
"""

# Convert the result to a Python object if needed
# print(result.r_repr())
