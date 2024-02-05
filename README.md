# PM25-Clustering
[Polimi WiSe 2023/24] Clustering of weekly PM2.5 Data


# Using Python-wrapped R-Code

## Installation of the ppmSuite to use
Since we need the compiled binary files, we first install the R command line tools

```shell
brew install r
```

and in a second step we install the ppmSuite from source

```shell
R
install.packages("https://cran.r-project.org/src/contrib/ppmSuite_0.3.4.tar.gz")
```

[Documentation](https://cran.r-project.org/web/packages/ppmSuite/ppmSuite.pdf) of the package and
[R-link](https://cran.r-project.org/web/packages/ppmSuite/index.html).

## Installation of the drpm-Package
We use the ``devtools`` package to install the ``drpm``-package directly from github, via

```r
library(devtools)
install_github("https://github.com/gpage2990/drpm")
```

or install it directly in python
```python
from rpy2.robjects.packages import importr

utils = importr('utils')
utils.install_packages("devtools") # select appropriate mirror, e.g. 37
utils.install_packages("ppmSuite")

dev = importr("devtools")
dev.install_github("https://github.com/gpage2990/drpm")
```

[Github-site](https://github.com/gpage2990/drpm) of the package

# Use the provided software
Install required packages

```shell
pip install -r requirements.txt
```

Run the main-file with your experiment
```shell
python main.py
```


## DRPM-Clustering
We provide two files:
1. ``analyze_drpm.py``: used to run all large experiments and create the tables of the report
1. ``plots_drpm.py``: used to plot the results and visualize the clustering