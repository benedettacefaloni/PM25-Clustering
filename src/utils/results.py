import numpy as np
import pandas as pd
import rpy2.robjects.packages as rpackages
from sklearn.metrics import adjusted_rand_score

from utils.data_loader import to_r_matrix, to_r_int_vector
from utils.models import get_fitted_attr_name

salso = rpackages.importr("salso")

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
    "max_pm25_diff",
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
    "mse": np.average,
    "n_singletons": np.max,
    # maybe maximum?
    "n_clusters": np.average,
    "max_cluster_size": np.max,
    "min_cluster_size": np.min,
    # TODO: check this
    "mean_cluster_size": np.max,
    "mode_cluster_size": np.max,
    "max_pm25_diff": np.max,
}


class YearlyPerformance:
    def __init__(
        self,
        config: dict,
        weekly_results: list = None,
        yearly_result_decomposed: dict = None,
    ):
        self.config = config

        if weekly_results is None:
            self.list_of_weekly: dict = yearly_result_decomposed
        else:
            self.list_of_weekly: dict = self.combine_weekly_to_yearly(weekly_results)

    def combine_weekly_to_yearly(self, weekly_results: list) -> dict:
        res = {}
        # aggregated values
        for key in kpis:
            res[key] = np.array([week[key] for week in weekly_results])

        # partition has the shape (n_timesteps, n_stations), i.e. each row is a partition per timestep
        res["partition"] = np.array(
            [week["salso_partition"] for week in weekly_results]
        )
        try:
            res["alpha"] = np.array([week["alpha"] for week in weekly_results])
        except:
            pass

        return res

    def aggegrate_weekly_to_yearly(self) -> dict:
        """
        Aggregate the weekly data (dict each) into yearly values.
        Decide for each attribute how to aggregate.
        """
        res = {}
        # aggregated values
        for key, agg_func in agg_mapping.items():
            if isinstance(self.list_of_weekly[key], float):
                res[key] = self.list_of_weekly[key]
            else:
                res[key] = agg_func([week for week in self.list_of_weekly[key]])

        # partition has the shape (n_timesteps, n_stations), i.e. each row is a partition per timestep
        res["partition"] = np.array([week for week in self.list_of_weekly["partition"]])

        return res

    def __repr__(self) -> str:
        cust_str = "Performance: \n\t - WAIC: {:4.2f}\n\t - LPML: {:4.2f}\n\t - MSE:  {:4.2f}".format(
            np.max(self.list_of_weekly["waic"]),
            np.max(self.list_of_weekly["lpml"]),
            np.max(self.list_of_weekly["mse"]),
        )
        return cust_str

    def to_table_row(self, select_params: list[str], index: [int]):
        yearly = self.aggegrate_weekly_to_yearly()
        select = [
            "lpml",
            "waic",
            "time",
            "mse",
            "n_singletons",
            "n_clusters",
            "max_cluster_size",
            "min_cluster_size",
            "max_pm25_diff",
        ]
        yearly_select = {key: yearly[key] for key in select}
        params = {key: self.config[key] for key in select_params}
        return pd.DataFrame(params | yearly_select, index=index)


def select_params_based_on_method(method_name: str):
    if method_name == "sppm":
        return ["cohesion", "M"]
    elif method_name == "gaussian_ppmx":
        return ["meanModel", 
                "cohesion",
                #"M", #the precision paramter M does not influence anything 
                "PPM",
                "similarity_function", 
                "consim",
                "calibrate"]
    elif method_name == "drpm":
        return [
            "M",
            "starting_alpha",
            # "alpha_0",
            # "eta1_0",
            # "phi1_0",
            "SpatialCohesion",
        ]
    else:
        raise NotImplementedError


class ModelPerformance:
    def __init__(self, name: str):
        self.name = name
        self.test_cases: list[YearlyPerformance] = []

    def add_testcase(
        self, yearly_result: YearlyPerformance, show_to_console: bool = False
    ):
        if show_to_console:
            print(yearly_result)
        self.test_cases.append(yearly_result)

    def to_table(self, select_params: list[str] = None) -> pd.DataFrame:
        """Create a table for each test case of the model, i.e. a complete overview.

        Parameters
        ----------
        select_params : list[str], optional
            List of parameter names that were varied during the training and should
            therefore be displayed in the table to uniquely identify a model.

        Returns
        -------
        pd.DataFrame
            Table with all tested models.
        """
        if select_params is None:
            select_params = select_params_based_on_method(self.name)
        table = self.test_cases[0].to_table_row(select_params, index=[0])
        for idx in range(1, len(self.test_cases)):
            table = pd.concat(
                [table, self.test_cases[idx].to_table_row(select_params, index=[idx])],
                ignore_index=True,
            )
        table["Model"] = self.name
        return table


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
        target = np.array(target)
        analysis["mse"] = MSE(
            target=target,
            # we use the mean of the MCMC samples to estimate the prediction value
            prediction=py_res[get_fitted_attr_name(model_name=model_name)].mean(axis=0),
            axis=0,
        )

        try:
            analysis["alpha"] = np.average(py_res["alpha"])
            analysis["alpha_std"] = np.std(py_res["alpha"])
        except:
            pass

        # analyse number of cluster distribution
        salso_partition = np.array(
            salso.salso(
                to_r_matrix(py_res["Si"]),
                **salso_args,
            )
        )

        # analyse time-dependency of partitions with lagged ARI values
        analysis["salso_partition"] = salso_partition
        analysis["max_pm25_diff"] = max_pm25_diff_per_cluster(target, salso_partition)

        unique, counts = np.unique(salso_partition, return_counts=True)
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
        analysis["alpha"] = py_res["alpha"].mean(axis=0)
        analysis["alpha_std"] = py_res["alpha"].std(axis=0)

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

        analysis["laggedRI"] = laggedRI(
            firstweek=1, lastweek=52, salso_pars=analysis["partition"]
        )
        analysis["laggedARI"] = laggedARI(
            firstweek=1, lastweek=52, salso_pars=analysis["partition"]
        )

        # decompose the yearly clustering into weekly chunks for detailed analysis
        analysis["max_pm25_diff"] = []
        for kpi in cluster_size_weekly_kpi.keys():
            analysis[kpi] = []

        for week in range(num_weeks):
            unique, counts = np.unique(
                analysis["partition"][week, :], return_counts=True
            )

            analysis["max_pm25_diff"].append(
                max_pm25_diff_per_cluster(
                    target[:, week], analysis["partition"][week, :]
                )
            )

            for key, lam_eval in cluster_size_weekly_kpi.items():
                analysis[key].append(lam_eval(unique=unique, counts=counts))
        return analysis


def MSE(target: np.ndarray, prediction: np.ndarray, axis: int):
    return ((target - prediction) ** 2).mean(axis=axis)


def max_pm25_diff_per_cluster(target: np.ndarray, salso_partition: np.array):
    return max(
        [
            (
                target[np.where(salso_partition == i)].max()
                - target[np.where(salso_partition == i)].min()
            )
            # cluster labels start at value 1
            for i in range(1, np.amax(salso_partition) + 1)
        ]
    )


def laggedRI(firstweek: int, lastweek: int, salso_pars: np.array):
    len = lastweek - firstweek + 1
    RImatrix = np.zeros((len, len))
    for i in range(len):
        for j in range(i + 1):
            ri = salso.RI(
                to_r_int_vector(salso_pars[i]), to_r_int_vector(salso_pars[j])
            )[0]
            RImatrix[i, j] = ri
            RImatrix[j, i] = ri
    return RImatrix


def laggedARI(firstweek: int, lastweek: int, salso_pars: np.array):
    len = lastweek - firstweek + 1
    ARImatrix = np.zeros((len, len))
    for i in range(len):
        for j in range(i + 1):
            ari = adjusted_rand_score(salso_pars[i], salso_pars[j])
            ARImatrix[i, j] = ari
            ARImatrix[j, i] = ari
    return ARImatrix
