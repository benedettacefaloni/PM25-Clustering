import numpy as np
import pandas as pd
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri

# Activate automatic conversion of pandas objects to R objects
# pandas2ri.activate()

# Import the drpm package
drpm = rpackages.importr("drpm")

# Simplify the call to the drpm_fit function
drpm_fit = drpm.drpm_fit

nobs = 10

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

# Spatial coordinates for prediction (s1p, s2p)
s_pred_test = np.random.uniform(0, 10, (nobs, 2))
s_pred = np.random.uniform(0, 10, nobs * 2)

# Cohesion value
cohesion = 1

# Create a dictionary with the data
# data = {"y": y, "s": s, "s.pred": s_pred, "cohesion": cohesion}
data = {"y": y, "s": s, "s.pred": s_pred}

print(ro.r["matrix"](ro.FloatVector(s), nrow=nobs))
s_float = ro.FloatVector(s)
test = ro.r["matrix"](s_float, nrow=int(nobs), ncol=2)
print(type(test))
print("here")

r_data_test = {
    "y": m,
    "s_coords": test,
    "starting_alpha": 0.1,
    # "cohesion": 1,
}
print("conversion worked")

# Call the simplified drpm_fit function
result = drpm_fit(**r_data_test)

# Convert the result to a Python object if needed
print(result)
# result_python = pandas2ri.ri2py(result)
