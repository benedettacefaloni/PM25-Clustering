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
- Add the documentation part into the section "Data Preparation
    and Initial Data Analysis" of the report
- Upload the original aggregation code onto Github

### Optional
- Repeat with another year (maybe a covid year) so we can later on work on a comparison


## Coding
- Decide on evaluation criteria
- General framework for automatic evaluation
- Prior parameter choice?

### Optional
- Streamlit application for interactive visualization

## Report
- Formulate the Introduction of the slides into text (explain pm2.5, causes, etc.)
- Integrate the data exploration part (see above)
- Theory and models part
    - Mathematical formulations
    - Pros and Cons and our expectations from the models
    - Explain priors and extensions in detail
    - Paper citations