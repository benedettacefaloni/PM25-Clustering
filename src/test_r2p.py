import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rpy2 import robjects
from rpy2.robjects.packages import data, importr

# Load the 'datasets' package and get the 'mtcars' dataset
datasets = importr("datasets")
ppmSuite = importr("ppmSuite")
drpm = importr("drpm")

print(ppmSuite.sppm)
print("ppmSuite worked")
print(drpm.drpm_fit)

print("worked")
