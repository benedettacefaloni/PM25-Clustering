import numpy as np
import rpy2.robjects.packages as rpackages

from utils.data_loader import to_r_matrix

salso = rpackages.importr("salso")


class YearlyResults:
    def __init__(
        self,
        name: str,
        config: dict,
        weekly_results: list = None,
        yearly_result: dict = None,
    ):
        self.name = name
        self.config = config

        if weekly_results is not None:
            self.yearly = self.aggegrate_weekly_to_yearly(weekly_results)
        else:
            self.yearly = self.analyse_yearly(yearly_result)

    def aggegrate_weekly_to_yearly(self, weekly_results):
        """
        Aggregate the weekly data (dict each) into yearly values.
        Decide for each attribute how to aggregate.
        """
        # TODO:
        # - find out if lower/higher is better
        # - compute the MSE
        agg_mapping = {
            "lpml": max,
            "waic": max,
            "n_singleton": max,
            "n_clusters": np.average,
            "n_clusters_max": max,
            "n_clusters_min": min,
        }

        res = {}
        # aggregated values
        for key, agg_func in agg_mapping.items():
            res[key] = agg_func([week[key] for week in weekly_results])

        # partition has the shape (n_timesteps, n_stations), i.e. each row is a partition per timestep
        res["partition"] = np.array(
            [week["salso_partition"] for week in weekly_results]
        )

        return res

    def analyse_yearly(self):
        pass


class Analyse:
    @staticmethod
    def analyze_weekly_result(
        py_res: dict, salso_args: dict = {"loss": "binder", "maxNCluster": 0}
    ) -> dict:
        """
        Aggregate one weekly result into a dict of aggregated values. Salso method is
        executed to reduce the MCMC iterates to a single partition.
        """
        analysis = {}
        analysis["lpml"] = py_res["lpml"]
        analysis["waic"] = py_res["WAIC"]

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
        return analysis

    @staticmethod
    def analyze_yearly_result(r_res, py_res: dict) -> dict:
        pass
