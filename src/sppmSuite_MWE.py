import numpy as np
import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri

# Minimal Working Example to call the sppm function in Python

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
    "y": ro.FloatVector([1, 1, 1]),
    # "s": s_coords,
    "s": ro.r["matrix"](ro.FloatVector([1, 1, 1, 1, 1, 1]), nrow=int(nobs), ncol=2),
    "cohesion": 2,
    # "M": 2,
    # "modelPriors": ro.FloatVector([0, 100**2, 10, 10]),
    # "cParms": ro.FloatVector([1, 1.5, 0, 1, 2, 2]),
    # "mh": ro.FloatVector([0.5, 0.5]),
    # "draws": 10000,
    # "burn": 100,
    # "thin": 10,
}

# Call the simplified drpm_fit function
result = ppmSuite.sppm(**r_data_test)
print("worked")

# Convert the result to a Python object if needed
# print(result.r_repr())
# result_python = pandas2ri.ri2py(result)
