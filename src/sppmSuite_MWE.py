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

# Spatial coordinates (s1, s2)
s = np.random.uniform(0, 10, nobs * 2)
s_float = ro.FloatVector(s)
s_coords = ro.r["matrix"](s_float, nrow=int(nobs), ncol=2)

print("data")
r_data_test = {
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

result = ppmSuite.sppm(**r_data_test)
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
