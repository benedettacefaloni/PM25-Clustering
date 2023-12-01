# Roadmap for the Project

## Data Preparation

- Decide on year
- Filter NaN values out
- Document the loss of data and why the specific year was chosen 
- Integrate week number into the columns
- Save filtered and cleaned data as a new table

- Integrate into data loader to easily filter the data by week
    - write subfunctions to provide data for sppm (weekly) and drpm (full time-series,
    reshape to n_stations, time with increasing values)
- Document the aggregation
- Add the documentation part into the section "Data Preparation
    and Initial Data Analysis" of the report
- Upload the the code which created the aggregation onto Github

Backlog:
- Standardize data for the covariates
    - categorical data?
- Fix issue with week numbers in year 2021

### Optional
- Repeat with another year (maybe a covid year) so we can later on work on a comparison


## Coding
- Decide on evaluation criteria
    - MSE on the prediction values (lower is better)
    - WAIC lower/higher better?
    - LPML lower/higher better?
    - [DONE] number of cluster overall
    - [DONE] sizes of clusters
        - number of singleton clusters
        - min, max, avg, median size
    - max. distance between two stations in the same cluster
    - plot the number of clusters for different methods over time in a grid-wise fashion

- Manual checking
    - Plot clusters with a map
    - Switching of a single station

- [Done] General framework for automatic evaluation

- Next steps 30.11.2023:
    - error in the drpm method
    - covariate transformation
    - gaussian_ppmx --> covariates
    - provide a MWE for a single method to plot and test the results
    - Finish evaluation: table creation

- Prior parameter choice?
    - SPPM:
        - M: different values 5*10e-3, 0.01, 0.1, 1.0
        - m = 0, s2 = 10^2, B = 10, A = 10 (page 27 in the reader)
        - C1:
            - alpha: 1.0 and 2.0
        - C2:
            - median distance of all pairwise distances (p. 9 in the reader)
        - C3 and C4:
            - mu0 - center of NNIG for cohesion 3 and 4
            - k0 - scale parm of gaussian part of NNIG for cohesion 3 and 4
            - v0 - degrees of freedom IG part of NNIG for cohesion 3 and 4
            - L0 - scale parm (scalar of identity matrix) IG part of NNIG for cohesion 3 and 4
    - ppmx
        - v is the kappa since we standardized the Covariates
        - (m0 = 0, k0 = 1.0,v0 = 10.0, n0 = 2)
        - and the second (m0 = 0, k0 = 1.0,v0 = 1.0, n0 = 2)
    - tRPM:
        - A_sigma = 5 or 0.5*sd(Yvec) (temporally indipendent CRP and temporally static CRP) or 1 (Space-time data generation) or 15 (2 to account for the higher variability present in the data)
        - A_tau = 10 or 100  (temporally indipendent CRP and temporally static CRP) or 2 (Space-time data generation)
        - A_lambda = 10
        - m0 = 0
        - S0 = 100
        - a_alpha = b_alpha = M = 1
        - alpha(t) = alpha 
            - alpha: 1.0 and 2.0 (lead to similar results)

- [DONE] Use salso package to evaluate the clustering itself
- implement visualization method for report and sanity checks
    - plot pm2.5 concentration and clustering at the same time

### Optional
- Streamlit application for interactive visualization
    - over time
    - values for params of the methods (input is a dict with prewritten values in a text field)
    - see: https://streamlit.io/ for more details, the deployment is free to host the app

## Report
- Formulate the Introduction of the slides into text (explain pm2.5, causes, etc.)
- Integrate the data exploration part (see above)
- Theory and models part
    - Mathematical formulations
    - Pros and Cons and our expectations from the models
    - Explain priors and extensions in detail
    - Paper citations

Backlog:
- Salso Package: give short insights about the methods idea
- Give theoretical details about the evaluation criteria used in the report, indicate if higher/lower is better (always in brackets)
    - e.g. MSE = mean squared error (lower is better)
- Cite R packages
