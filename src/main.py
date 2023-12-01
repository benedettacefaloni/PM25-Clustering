import rpy2.robjects as ro

from utils.clustering import Cluster
from utils.data_loader import load_data, yearly_data_as_timeseries
from utils.models import Model
from utils.results import Analyse, ModelResults, YearlyResults
from utils.visualize import trace_plots


def main():
    data = load_data()
    pm25_timeseries = yearly_data_as_timeseries(data)

    salso_args = {"loss": "binder", "maxNCluster": 0}

    sppm_args = {
        "cohesion": 2,
        "M": 2,
        "modelPriors": ro.FloatVector([0, 100**2, 10, 10]),
        "cParms": ro.FloatVector([1, 1.5, 0, 1, 2, 2]),
        "mh": ro.FloatVector([0.5, 0.5]),
        "draws": 10000,
        "burn": 100,
        "thin": 10,
    }
    drpm_args = {
        "M": 2,
        "starting_alpha": 0.5,  # 0.1
        "unit_specific_alpha": False,
        "time_specific_alpha": False,
        "alpha_0": False,
        "eta1_0": False,
        "phi1_0": False,
        "modelPriors": ro.FloatVector([0, 100**2, 1, 1, 1, 1]),
        "alphaPriors": ro.r["matrix"](ro.FloatVector([1, 1]), nrow=1),
        "simpleModel": 0,
        "theta_tau2": ro.FloatVector([0, 2]),
        "SpatialCohesion": 4,
        "cParms": ro.FloatVector([0, 1, 2, 1]),
        "mh": ro.FloatVector([0.5, 1, 0.1, 0.1, 0.1]),
        "verbose": False,
        "draws": 10000,
        "burn": 100,
        "thin": 10,
    }

    num_weeks = 2

    model = (Model("sppm", sppm_args, uses_weekly_data=True),)
    # model = Model("drpm", drpm_args, uses_weekly_data=False),

    all_results: list[ModelResults] = []

    model_result = ModelResults(name=model.name)
    for model_params in model.yield_test_cases():
        if model.uses_weekly_data:
            weekly_results = []
            for week in range(1, num_weeks):
                week_data = data[data["Week"] == week]

                model_args = model_params | model.load_model_specific_data(week_data)
                res_cluster, time_needed = Cluster.cluster(
                    model=model.name, **model_args
                )
                weekly_results.append(
                    Analyse.analyze_weekly_result(
                        py_res=res_cluster,
                        target=week_data["log_pm25"],
                        time_needed=time_needed,
                        salso_args=salso_args,
                    )
                )
            yearly_result = YearlyResults(
                config=model_params, weekly_results=weekly_results
            )

        else:
            # use yearly data
            model_args = model_params | model.load_model_specific_data(
                data=data, yearly_time_series=pm25_timeseries
            )
            res_cluster, time_needed = Cluster.cluster(model=model.name, **model_args)
            yearly_result = YearlyResults(
                config=model_params,
                yearly_result=Analyse.analyze_yearly_result(
                    py_res=res_cluster,
                    target=pm25_timeseries,
                    time_needed=time_needed,
                    salso_args=salso_args,
                ),
            )
        model_result.add_testcase(yearly_result=yearly_result)
    all_results.append(model_result)


if __name__ == "__main__":
    main()
