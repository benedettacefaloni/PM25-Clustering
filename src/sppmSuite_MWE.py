import numpy as np
import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri

# Activate automatic conversion of pandas objects to R objects
# pandas2ri.activate()

# Import the drpm package
ppmSuite = rpackages.importr("ppmSuite")
nobs = 100

# Response variable (y)
y = np.random.normal(0, 1, nobs)
v = ro.FloatVector(y)

n_cov = 10
X_py = np.random.normal(0, 20, size=(nobs, n_cov))
X = ro.r["matrix"](ro.FloatVector(X_py), nrow=int(nobs), ncol=n_cov)


# Spatial coordinates (s1, s2)
s = np.random.uniform(0, 10, nobs * 2)
s_float = ro.FloatVector(s)
s_coords = ro.r["matrix"](s_float, nrow=int(nobs), ncol=2)

print("data")
sppm_args = {
    "y": v,
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
gaussian_ppmx_args = {
    "y": v,
    "X": X,
    "meanModel": 1,
    "cohesion": 1,
    "M": 2,
    "PPM": False,  # use covariates if FALSE -> supply X
    "similarity_function": 1,
    "consim": 1,
    "calibrate": 0,
    "simParms": ro.FloatVector([0.0, 1.0, 0.1, 1.0, 2.0, 0.1, 1]),
    "modelPriors": ro.FloatVector([0, 100**2, 1, 1]),
    "mh": ro.FloatVector([0.5, 0.5]),
    "draws": 10000,
    "burn": 100,
    "thin": 10,
    "verbose": False,
}

sppm_res = ppmSuite.sppm(**sppm_args)
ppmx_res = ppmSuite.gaussian_ppmx(**gaussian_ppmx_args)
print("worked")
"""The result is of the following structure:
    - Mu double [990 x 6]
    - sig2 double [990 x 6]
    - Si integer (990 x 6]
    - like double [990 x 6]
    - fitted double [990 x 6]
    - ppred double [990 x 0]
    - muO double [990]
    - sig20 double [990]
    - nclus integer [990]
    - WAIC double [1]
    - Ipmi double [1]
"""

# Convert the result to a Python object if needed
# print(result.r_repr())
