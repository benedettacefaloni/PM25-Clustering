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

### Optional
- Repeat with another year (maybe a covid year) so we can later on work on a comparison


## Coding
- Decide on evaluation criteria
    - MSE on the prediction values

- General framework for automatic evaluation
- Prior parameter choice?
    - SPPM:
        - M: different values 5*10e-3, 0.01, 0.1, 1.0
        - C1:
            - alpha: 1.0 and 2.0
        - C2:
    - tRPM:
        - A_sigma = 5 or 0.5*sd(Yvec) (temporally indipendent CRP and temporally static CRP) or 1 (Space-time data generation) or 15 (2 to account for the higher variability present in the data)
        - A_tau = 10 or 100  (temporally indipendent CRP and temporally static CRP) or 2 (Space-time data generation)
        - A_lambda = 10
        - m0 = 0
        - S0 = 100
        - a_alpha = b_alpha = M = 1
        - alpha(t) = alpha 

- Use salso package to evaluate the clustering itself
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
