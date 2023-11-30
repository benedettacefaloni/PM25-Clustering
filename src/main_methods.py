import rpy2.robjects as ro

from utils import Cluster
from utils.data_loader import load_data, yearly_data_as_timeseries
from utils.methods import Method
from utils.results import Analyse, YearlyResults


def main():
    data = load_data()
    pm25_timeseries = yearly_data_as_timeseries(data)

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
        "starting_alpha": 0.1,
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
    methods = [
        Method("sppm", sppm_args, uses_weekly_data=True),
        # Method("gaussian_ppmx", sppm_args, uses_weekly_data=True),
        Method("drpm", drpm_args, uses_weekly_data=False),
    ]

    for method in methods:
        for test_case in method.yield_test_cases():
            if method.uses_weekly_data:
                weekly_results = []
                for week in range(1, 10):
                    week_data = data[data["Week"] == week]

                    method_args = test_case | method.load_method_specific_data(
                        week_data
                    )
                    res_cluster = Cluster.cluster(method=method.name, **method_args)
                    weekly_results.append(Analyse.analyze_weekly_result(res_cluster))
                test = YearlyResults(
                    method.name, test_case, weekly_results=weekly_results
                )
                print(test.yearly)
            else:
                # use yearly data
                method_args = test_case | method.load_method_specific_data(
                    data=data, yearly_time_series=pm25_timeseries
                )
                res_cluster = Cluster.cluster(method=method.name, **method_args)


if __name__ == "__main__":
    main()
