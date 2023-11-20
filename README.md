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

[Github-site](https://github.com/gpage2990/drpm) of the package
