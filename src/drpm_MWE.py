import numpy as np
import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri

from utils import Cluster

# Activate automatic conversion of pandas objects to R objects
# pandas2ri.activate()

# Import the drpm package
drpm = rpackages.importr("drpm")

# Simplify the call to the drpm_fit function
drpm_fit = drpm.drpm_fit

n_obs = 10

# Response variable (y)
n_stations = 3
n_timesteps = 3

y_test = np.random.uniform(0, 1, size=(n_stations, n_obs))

y_test = np.array(
    [
        [31.85714286],
        [25.42857143],
        [26.85714286],
        [38.14285714],
        [23.42857143],
        [20.42857143],
        [34.85714286],
        [34.0],
        [33.42857143],
        [19.42857143],
    ]
)
s = np.array(
    [
        [46.1678524, 9.87920992],
        [46.1678524, 9.87920992],
        [46.1678524, 9.87920992],
        [46.1678524, 9.87920992],
        [46.1678524, 9.87920992],
        [46.1678524, 9.87920992],
        [46.1678524, 9.87920992],
        [46.1678524, 9.87920992],
        [46.1678524, 9.87920992],
        [46.1678524, 9.87920992],
    ]
)

# y_test = [1, 1, 1, 2, 2, 2]

print("y_test.shape = ", y_test.shape)
print(y_test.shape)
v = ro.FloatVector(y_test)
m = ro.r["matrix"](v, nrow=1)
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

res = Cluster.cluster(method="drpm", **r_data_test)
print(res.keys())
# Call the simplified drpm_fit function
result = drpm_fit(**r_data_test)
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
