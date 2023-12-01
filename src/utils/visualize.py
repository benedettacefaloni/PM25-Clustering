import os
from pathlib import Path

from tabulate import tabulate

report_path = os.path.join(Path(__file__).parent.parent.parent, "report/")


def experiment_to_table(filename: str, path: str = report_path):
    pass
