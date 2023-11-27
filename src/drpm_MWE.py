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

nobs = 100

# Response variable (y)
y = np.random.normal(0, 1, nobs)

y_test = [1, 1, 1, 1, 1, 1]
v = ro.FloatVector(y_test)
m = ro.r["matrix"](v, nrow=2)
print("m = ")
print(type(m))
print(m)

# Spatial coordinates (s1, s2)
s = np.random.uniform(0, 10, nobs * 2)
s_float = ro.FloatVector(s)
s_coords = ro.r["matrix"](s_float, nrow=int(nobs), ncol=2)

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
