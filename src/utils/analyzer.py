import numpy as np
import rpy2.robjects.packages as rpackages

salso = rpackages.importr("salso")


class Analyse:
    @staticmethod
    def analyze_weekly_result(r_res, py_res: dict) -> dict:
        analysis = {}
        analysis["lpml"] = py_res["lpml"]
        analysis["waic"] = py_res["WAIC"]

        # analyse number of cluster distribution
        salso_partion = np.array(salso.salso(r_res[2], loss="binder", maxNClusters=0))
        unique, counts = np.unique(salso_partion, return_counts=True)

        analysis["n_singleton"] = counts[counts == 1].shape[0]

        analysis["n_clusters_total"] = unique.shape[0]
        analysis["n_clusters_max"] = max(counts)
        analysis["n_clusters_min"] = min(counts)
        analysis["n_clusters_avg"] = np.mean(counts)
        analysis["n_clusters_mode"] = np.median(counts)
        return analysis

    @staticmethod
    def aggregate_weekly_to_yearly():
        """
        for method in method:
            for config in configurations:
                --> aggregate

        """
        pass

    @staticmethod
    def analyze_yearly_result(r_res, py_res: dict) -> dict:
        pass
