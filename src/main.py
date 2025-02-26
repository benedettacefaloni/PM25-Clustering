import logging #used to incorporate logging functionality into the script. Logging is a way to capture and store information about the program's execution, errors, warnings, and other messages. It's a standard practice for debugging and monitoring the behavior of your code.

import pandas as pd #importing the Pandas library. Pandas is a powerful library for data manipulation and analysis, and it provides data structures like DataFrames that are commonly used in data science and machine learning tasks. A DataFrame is a two-dimensional, tabular data structure in the Pandas library for Python. It is similar to a spreadsheet or SQL table, where data is arranged in rows and columns. Each column can have a different data type, and you can perform various operations on the data, such as filtering, grouping, and aggregation.
import rpy2.robjects as ro #imports the robjects module from the rpy2 library. rpy2 is a Python library that provides an interface to R, the statistical computing and graphics language. This library allows you to call R functions and use R objects directly from Python.

from utils.clustering import Cluster
from utils.data_loader import (
    all_covariates,
    get_covariates,
    get_numerical_covariates,
    load_data,
    to_r_dataframe,
    yearly_data_as_timeseries,
)
from utils.magic import set_r_python_seed
from utils.models import Model
from utils.results import Analyse, ModelPerformance, YearlyPerformance
from utils.tables import python_to_latex
from utils.visualize import (
    WeeklyClustering,
    YearlyClustering,
    param_distribution,
    plot_clustering,
    plot_weekly_clustering_kpi_overview,
    trace_plots,
)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None) #lines 27 and 28 have been added 
def main():
    set_r_python_seed() #the purpose of this function is to synchronize the random number generation seeds between NumPy (used in Python) and R. This synchronization is crucial for ensuring that both Python and R generate the same sequence of random numbers when required, contributing to the reproducibility of results. you are setting the seed for both the NumPy (Python) random number generator and the R random number generator. This ensures that the sequence of random numbers generated by these generators will be the same every time your code is run, providing reproducibility. In terms of output, there isn't any direct output or variable created that you can observe in the code. The effect of setting the seed becomes apparent when your code involves randomness, for example, in scenarios where you use random numbers or sampling. The purpose is to make your results reproducible. Without setting the seed, each run of your code could yield different results due to the inherent randomness involved in certain computations.For instance, if you have a part of your code that uses random numbers, setting the seed ensures that even though the numbers are technically random, they will be the same every time you run the code. This can be crucial for debugging, testing, and ensuring that others can obtain the same results when they run your code. 
    data = load_data() #loading your data from a CSV file, performing some data type conversions, and handling missing data. since i'm not providing any input value, i will considering the defalut ones, i.e. 2019 for the year and none for the week. having week = none means that i'm not filtering any specific week. since the load_dat function returns a pd.dataframe, data will be a Pandas DataFrame 
    pm25_timeseries = yearly_data_as_timeseries(data) # creating a matrix (pm25_timeseries) where each row represents the weekly pm2.5 values of one station over the entire year, and each column represents the pm2.5 values of all stations for a specific week. on the row i have the indexes of stations and the columns are teh time series for each specific station
    salso_args = {"loss": "binder", "maxNCluster": 0} #This line defines a dictionary named salso_args with two key-value pairs: "loss": "binder": This sets the value associated with the key "loss" to the string "binder". This suggests that there is a loss function involved, and it is specifically the "binder" loss function. "maxNCluster": 0: This sets the value associated with the key "maxNCluster" to the integer 0. This parameter seems to control the maximum number of clusters and is set to 0.

    sppm_args = { #sppm is the main function used to fit model with Guassian likelihood and spatial PPM as prior on partitions.
        "cohesion": [1, 2], #scalar that indicates which cohesion function to use: 1 for distance from centroids, 2 for upper bound, 3 for auxiliary similarity and 4 for double dipper similarity
        "M": [1e-8, 3], #parameter related to Dirichlet process scale or dispersion parameter. when we compute the cohesion unction we have c(S) = M * gamma(|S|)
        "modelPriors": ro.FloatVector([0, 100**2, 10, 10]),#Vector containing model prior values
        "cParms": ro.FloatVector([1, 1.5, 0, 1, 2, 2]), #The cParm vector contains values associated with the cohesion function. cParm = c(epsilon value - cohesion 1 only, distance bound - cohesion 2 only, mu0 - center of NNIG for cohesion 3 and 4, k0 - scale parm of gaussian part of NNIG for cohesion 3 and 4, v0 - degrees of freedom IG part of NNIG for cohesion 3 and 4, L0 - scale parm (scalar of identity matrix) IG part of NNIG for cohesion 3 and 4).
        "mh": ro.FloatVector([0.5, 0.5]), #Tuning standard deviations for metropolis updates for sigma2 and sigma20
        "draws": 10000, #Number of MCMC samples to collect
        "burn": 100, #Number of the MCMC samples discarded in the burn-in phase of the sampler
        "thin": 10, #The amount of thinning desired for the chain
    }

    gaussian_ppmx_args = {
        "meanModel": 1,  # type of mean model to be included in the likelihood. 1 means that we use cluster specific means with no covariates in the likelihood while 2 means cluster-specific intercepts and a global regression of the type Xbeta is included in the likelihood
        "cohesion": 2, #type of cohesion function for the PPMx prior. option 1 is for the cohesion function that connects with the Dirichlet process (c(S) = M * (|S| - 1)!) while option 2 is for the uniform cohesion function (c(S) = 1) 
        "M": 1, #precision parameter/ the default value is 1
        "PPM": False,  #Logical argument that indicates if the PPM or PPMx partition model should be employed. If PPM = FALSE, then an X matrix must be supplied (where the X matrix is a data frame whose columns consist of covariates that will be incorporated in the partition model. Those with class of "character" or "factor" will be treated as categorical covariates. All others will be treated as continuous covariates.)
        "similarity_function": 4,
        "consim": 2,
        "calibrate": 2,
        "simParms": ro.FloatVector([0.0, 1.0, 0.1, 1.0, 2.0, 0.1, 1]), #the second to last parameter is the dirichlet weight for categorical similarity with default of 0.1 (smaller values place more weight on partitions with individuals that are in the same category.) indeed, as reported in the reference "Calibrating covariate...", when we have categorical covariates, it is natural to use a Multinomial-Dirichlet conjugate pairing resulting in a Multinomial for the q(.|.) and a Dirichlet for q(.). indeed, q(.) = Dirichlet (pi|alphaj) and this is exaclty that alphaj (for whcih we are following the suggestions of Muller et al, setting it to a C-dimensional vector of 0.1 where C is the number of covariates)
        "modelPriors": ro.FloatVector([0, 100**2, 10, 10]),
        "mh": ro.FloatVector([0.5, 0.5]), # vector used for tuning the Metropolis-Hastings updates for specific parameters in the Markov Chain Monte Carlo (MCMC) algorithm. The mh vector has two elements, and each element corresponds to a specific tuning parameter associated with an MH update. Let's break down the details of the mh vector: "mh": ro.FloatVector([0.5, 0.5]) First Element (0.5): This value represents the tuning parameter associated with the Metropolis-Hastings update for the parameter sigma2. sigma2 likely corresponds to some variance parameter in the model. The value of 0.5 is a starting point for the tuning parameter. The specific value of this tuning parameter affects the step size or proposal distribution in the Metropolis-Hastings algorithm. A higher value would result in larger steps, while a lower value would result in smaller steps. Second Element (0.5): This value represents the tuning parameter associated with the Metropolis-Hastings update for the parameter sigma20. Similarly, sigma20 likely corresponds to another variance parameter in the model. Like the first element, the value of 0.5 is a starting point for tuning the Metropolis-Hastings update for sigma20. In summary, the mh vector provides the initial values for tuning parameters that control the step sizes in the Metropolis-Hastings updates for specific parameters (sigma2 and sigma20) during the MCMC sampling process. Fine-tuning these parameters is crucial for achieving an effective and efficient MCMC sampling process, ensuring that the algorithm explores the parameter space effectively and converges to the target distribution. Adjusting these tuning parameters may be necessary based on the characteristics of the specific model and data being analyzed.
        "draws": 1100,
        "burn": 100,
        "thin": 1,
        "verbose": False,
    }
    drpm_args = {
        "M": 100,
        "starting_alpha": 0.75,  # 0.5
        "unit_specific_alpha": False,
        "time_specific_alpha": False,
        "alpha_0": False,
        "eta1_0": False,
        "phi1_0": False,
        # "modelPriors": ro.FloatVector([0, 100**2, 1, 1, 1, 1]),
        "modelPriors": ro.FloatVector([0, 100**2, 10, 5, 5, 1]),
        # "modelPriors": ro.FloatVector([0, 100 * 2, 0.1, 1, 1, 1]),
        "alphaPriors": ro.r["matrix"](ro.FloatVector([1, 1]), nrow=1),
        "simpleModel": 0,
        "theta_tau2": ro.FloatVector([0, 2]),
        "SpatialCohesion": 4,
        "cParms": ro.FloatVector([0, 1, 2, 1]),
        "mh": ro.FloatVector([0.5, 1, 0.1, 0.1, 0.1]),
        "verbose": False,
        "draws": 10000,
        "burn": 1000,
        "thin": 10,
    }

    num_weeks = 53
    # num_weeks = 3

    # model = Model("sppm", sppm_args, uses_weekly_data=True)
    model = Model("gaussian_ppmx", gaussian_ppmx_args, uses_weekly_data=True)
    # model = Model("drpm", drpm_args, uses_weekly_data=False)

    all_results: list[ModelPerformance] = [] #The all_results variable is a list that is intended to store instances of the ModelPerformance class. It is initialized as an empty list.
    model_result = ModelPerformance(name=model.name) #creating an instance of the model performance class and assigning to the variable model_result. I'm calling here the constructor (initializer) of the ModelPerformance class. The name parameter is set to the name of the model, which is obtained from model.name (gaussian_ppmx in my case)
    #so now model result is an instance of the ModelPerformance class with the name attribute equal to gaussian_ppmx and the test_cases attribute equal to an empty list of elements belonging to the YearlyPerfromance class 
    for model_params in model.yield_test_cases(): #model.yield_test_cases() is a generator function that yields different combinations of parameter values for your model. Each iteration of the loop (for model_params in model.yield_test_cases():) assigns model_params the value yielded by the generator, which is a dictionary representing a specific combination of parameters. So, model_params is a dictionary, and each iteration of the loop corresponds to a different combination of parameter values for your model. Inside the loop, you can access and use the individual parameter values using keys from the model_params dictionary
        if model.uses_weekly_data: #we enter in this if bc we are considering gaussian_ppmx. the only one for which we do not use weekly data is drpm. WHY???
            save_to_visualize_cluster = WeeklyClustering() #creating an instance of the WeeklyClustering class and assigning it to the variable save_to_visualize_cluster.
        
            weekly_results = []
            for week in range(1, num_weeks):
                logging.info("Week {}/{}".format(week, num_weeks)) #logging informational messages. These messages are typically used for general information about the program's execution. Indeed I have imported the logging library at the beginning 
                week_data = data[data["Week"] == week]

                week_cov_rdf = get_covariates(
                    week_data.copy().drop(columns=["Week"]),
                    as_r_df=True,
                    only_numerical=False,
                )

                model_args = model_params | model.load_model_specific_data(
                    week_data, covariates=week_cov_rdf, model_params=model_params
                )
                res_cluster, time_needed = Cluster.cluster(
                    model=model.name, **model_args
                )
                weekly_res = Analyse.analyze_weekly_performance(
                    py_res=res_cluster,
                    target=week_data["log_pm25"],
                    time_needed=time_needed,
                    salso_args=salso_args,
                    model_name=model.name,
                )

                # save the results for visualization
                save_to_visualize_cluster.add_week(
                    week_number=week, weekly_data=week_data, weekly_res=weekly_res
                )
                # plot the param distribution: trace plots and histograms
                # param_distribution(res_cluster, model.name)

                # save the results for performance evaluation
                weekly_results.append(weekly_res)

            # aggregate the performance metrics
            yearly_result = YearlyPerformance(
                config=model_params, weekly_results=weekly_results
            )

        else:
            # use yearly data
            model_args = model_params | model.load_model_specific_data(
                data=data, yearly_time_series=pm25_timeseries, model_params=model_params
            )
            res_cluster, time_needed = Cluster.cluster(model=model.name, **model_args)
            yearly_result = YearlyPerformance(
                config=model_params,
                yearly_result_decomposed=Analyse.analyze_yearly_performance(
                    py_res=res_cluster,
                    target=pm25_timeseries,
                    time_needed=time_needed,
                    salso_args=salso_args,
                ),
            )
            save_to_visualize_cluster = YearlyClustering(
                yearly_decomposed_result=yearly_result, data=data
            )
            print(yearly_result.list_of_weekly["waic"])
            print(yearly_result.list_of_weekly["lpml"])

        # plot_weekly_clustering_kpi_overview(
        #     yearly_result=yearly_result, num_weeks=num_weeks
        # )
        model_result.add_testcase(yearly_result=yearly_result, show_to_console=True)
    plot_clustering(save_to_visualize_cluster, method_name=model.name)
    print("Model results as table: ")
    test = model_result.to_table()
    print(test)
    # print(
    #     python_to_latex(
    #         test, cols_to_min=["time"], cols_to_max=["waic"], filename="Test"
    #     )
    # )
    all_results.append(model_result)

if __name__ == "__main__":
    main()
