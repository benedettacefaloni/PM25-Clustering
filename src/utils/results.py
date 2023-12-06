import numpy as np
import rpy2.robjects.packages as rpackages

from utils.data_loader import to_r_matrix
from utils.models import get_fitted_attr_name

salso = rpackages.importr("salso")

# TODO:
# - find out if lower/higher is better
# available values to analyze
kpis = [
    "lpml",
    "waic",
    "time",
    # maybe yearly
    "mse",
    "n_singletons",
    "n_clusters",
    "max_cluster_size",
    "min_cluster_size",
    "mean_cluster_size",
    "mode_cluster_size",
]

# how to evaluate a weekly clustering
cluster_size_weekly_kpi = {
    "n_singletons": lambda unique, counts: counts[counts == 1].shape[0],
    "n_clusters": lambda unique, counts: unique.shape[0],
    "max_cluster_size": lambda unique, counts: np.max(counts),
    "min_cluster_size": lambda unique, counts: np.min(counts),
    "mean_cluster_size": lambda unique, counts: np.mean(counts),
    "mode_cluster_size": lambda unique, counts: np.median(counts),
}
# how to aggregate from weekly to yearly
agg_mapping = {
    "lpml": max,
    "waic": max,
    "time": np.sum,
    # maybe yearly
    "mse": max,
    "n_singletons": np.max,
    "n_clusters": np.average,
    "max_cluster_size": np.max,
    "min_cluster_size": np.min,
    # TODO: check this
    "mean_cluster_size": np.max,
    "mode_cluster_size": np.max,
}


class YearlyPerformance:
    def __init__(
        self,
        config: dict,
        weekly_results: list = None,
        yearly_result_decomposed: dict = None,
    ):
        self.config = config

        if weekly_results is not None:
            self.list_of_weekly = self.combine_weekly_to_yearly(weekly_results)
        else:
            self.list_of_weekly = yearly_result_decomposed

    def combine_weekly_to_yearly(self, weekly_results: list) -> dict:
        res = {}
        # aggregated values
        for key in kpis.keys():
            res[key] = np.array([week[key] for week in weekly_results])

        # partition has the shape (n_timesteps, n_stations), i.e. each row is a partition per timestep
        res["partition"] = np.array(
            [week["salso_partition"] for week in weekly_results]
        )

        return res

    def aggegrate_weekly_to_yearly(self, weekly_results: list) -> dict:
        """
        Aggregate the weekly data (dict each) into yearly values.
        Decide for each attribute how to aggregate.
        """
        res = {}
        # aggregated values
        for key, agg_func in agg_mapping.items():
            res[key] = agg_func([week[key] for week in weekly_results])

        # partition has the shape (n_timesteps, n_stations), i.e. each row is a partition per timestep
        res["partition"] = np.array(
            [week["salso_partition"] for week in weekly_results]
        )

        return res

    def to_table_row(self):
        # TODO
        pass


class ModelPerformance:
    def __init__(self, name: str):
        self.name = name
        self.test_cases: list[YearlyPerformance] = []

    def add_testcase(self, yearly_result: YearlyPerformance):
        self.test_cases.append(yearly_result)


class Analyse:
    @staticmethod
    def analyze_weekly_performance(
        py_res: dict,
        target: np.ndarray,
        time_needed: float,
        model_name: str,
        salso_args: dict = {"loss": "binder", "maxNCluster": 0},
    ) -> dict:
        """
        Aggregate one weekly result into a dict of aggregated values. Salso model is
        executed to reduce the MCMC iterates to a single partition.
        """
        analysis = {}
        analysis["lpml"] = py_res["lpml"]
        analysis["waic"] = py_res["WAIC"]
        analysis["mse"] = MSE(
            target=np.array(target),
            # we use the mean of the MCMC samples to estimate the prediction value
            prediction=py_res[get_fitted_attr_name(model_name=model_name)].mean(axis=0),
            axis=0,
        )

        # analyse number of cluster distribution
        salso_partion = np.array(
            salso.salso(
                to_r_matrix(py_res["Si"]),
                **salso_args,
            )
        )
        analysis["salso_partition"] = salso_partion

        unique, counts = np.unique(salso_partion, return_counts=True)
        # init the results and fill with evaluation function
        for key in cluster_size_weekly_kpi.keys():
            analysis[key] = []

        for key, lam_eval in cluster_size_weekly_kpi.items():
            analysis[key].append(lam_eval(unique=unique, counts=counts))

        analysis["time"] = time_needed
        return analysis

    @staticmethod
    def analyze_yearly_performance(
        py_res: dict,
        target: np.ndarray,
        time_needed: float,
        salso_args: dict = {"loss": "binder", "maxNCluster": 0},
    ) -> dict:
        analysis = {}
        analysis["time"] = time_needed

        analysis["lpml"] = py_res["lpml"]
        analysis["waic"] = py_res["waic"]

        # analyse the partitions for each week since salso cannot handle tensors
        SI_np = np.array(py_res["Si"])

        # weekly MSE, shape (n_weeks, n_stations)
        analysis["mse"] = MSE(
            target=target, prediction=py_res["fitted"].mean(axis=2).T, axis=0
        )

        num_weeks = SI_np.shape[0]
        analysis["partition"] = np.array(
            [
                np.array(
                    salso.salso(
                        to_r_matrix(SI_np[week, :, :].T),
                        **salso_args,
                    )
                )
                for week in range(num_weeks)
            ]
        )

        # decompose the yearly clustering into weekly chunks for detailed analysis
        for kpi in cluster_size_weekly_kpi.keys():
            analysis[kpi] = []

        for week in range(num_weeks):
            unique, counts = np.unique(
                analysis["partition"][week, :], return_counts=True
            )
            for key, lam_eval in cluster_size_weekly_kpi.items():
                analysis[key].append(lam_eval(unique=unique, counts=counts))
        return analysis


def MSE(target: np.ndarray, prediction: np.ndarray, axis: int):
    return ((target - prediction) ** 2).mean(axis=axis)
