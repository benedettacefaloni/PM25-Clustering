import numpy as np
import rpy2.robjects.packages as rpackages

from utils.data_loader import to_r_matrix
from utils.models import get_fitted_attr_name

salso = rpackages.importr("salso")

# TODO:
# - find out if lower/higher is better
agg_mapping = {
    "lpml": max,
    "waic": max,
    "time": np.sum,
    # maybe yearly
    "MSE": max,
    "n_singleton": max,
    "n_clusters": np.average,
    "n_clusters_max": max,
    "n_clusters_min": min,
}


class YearlyPerformance:
    def __init__(
        self,
        config: dict,
        weekly_results: list = None,
        yearly_result: dict = None,
    ):
        self.config = config

        if weekly_results is not None:
            self.yearly = self.aggegrate_weekly_to_yearly(weekly_results)
        else:
            self.yearly = yearly_result

    def aggegrate_weekly_to_yearly(self, weekly_results):
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
        analysis["MSE"] = MSE(
            target=np.array(target),
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

        analysis["n_singleton"] = counts[counts == 1].shape[0]
        analysis["n_clusters"] = unique.shape[0]
        analysis["n_clusters_max"] = max(counts)
        analysis["n_clusters_min"] = min(counts)
        analysis["n_clusters_avg"] = np.mean(counts)
        analysis["n_clusters_mode"] = np.median(counts)

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

        # weekly MSE
        mse = list(
            MSE(target=target, prediction=py_res["fitted"].mean(axis=2).T, axis=0)
        )

        # TODO: sth. does not work here
        analysis["partition"] = np.array(
            [
                np.array(
                    salso.salso(
                        to_r_matrix(SI_np[week, :, :].T),
                        **salso_args,
                    )
                )
                for week in range(SI_np.shape[0])
            ]
        )

        # apply along the zero-th (time)-axis
        unique, counts = np.unique(analysis["partition"], axis=0, return_counts=True)

        # TODO: evaluate the result
        # use the mapping above --> make it global

        return analysis


def MSE(target: np.ndarray, prediction: np.ndarray, axis: int):
    return ((target - prediction) ** 2).mean(axis=axis)
