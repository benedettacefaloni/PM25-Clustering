import logging
import time
from datetime import timedelta
from functools import partial, wraps

import numpy as np
import rpy2.robjects as ro

logging.basicConfig( #It configures a basic logging setup using logging.basicConfig. The logging level is set to INFO, which means it will display informational messages. The format includes a timestamp, log level, and the log message. The date format is set to include milliseconds.
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()


def set_r_python_seed(seed: int = 123): #This function sets the seed for both NumPy (Python) and R to ensure reproducibility in random number generation. It takes an optional argument seed with a default value of 123. I'm calling this function at line 31 in the main without an input value so i will use the default one which is 123 
    np.random.seed(seed) #This line sets the seed for the NumPy random number generator. Setting the seed ensures that the sequence of random numbers generated is reproducible, meaning that if you run the code with the same seed, you will get the same sequence of random numbers. We are calling the random module within the NumPy library. NumPy is a powerful library for numerical operations in Python, and its random module provides functions for generating random numbers. The seed method is used to initialize the random number generator with a particular seed. The seed is an integer value that determines the initial state of the random number generator. If you set the seed to the same value, you'll get the same sequence of random numbers every time you run the program.
    r = ro.r #This line creates a reference to the R instance in the robjects module. The robjects module provides an interface between Python and R. I'm assigning the R environment to the variable r for easier and shorter usage
    set_seed = r("set.seed") #This line creates a reference to the R function set.seed using the R instance (r). It essentially allows you to call the R function from Python. I'm creating a Python variable set_seed that refers to the R function set.seed.
    set_seed(seed) #This line calls the R function set.seed with the specified seed value. This is done through the set_seed reference obtained in the previous line. It sets the seed for the R random number generator, ensuring consistency between random number generation in Python (NumPy) and R. call to the R function set.seed with the argument seed. This is setting the seed for the random number generator in R. In the context of Bayesian analysis or any statistical modeling that involves randomness, setting the seed ensures reproducibility. When you set the seed for the random number generator, it means that the sequence of random numbers generated will be the same every time the code is run. This is important when you want to reproduce results or share your code with others


def log_time(func=None, get_time: bool = True, time_in_mins: bool = False): #This is a decorator function for logging the execution time of another function. It can be used as a decorator or as a regular function depending on whether func is None. The get_time parameter determines whether the execution time should be returned along with the result of the decorated function. The time_in_mins parameter specifies whether the time should be logged in minutes. It logs the time taken by the decorated function and returns the result and/or the execution time.
    if func is None:
        return partial(log_time, get_time=get_time)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            start = time.time()
            return_value = func(*args, **kwargs)
            time_needed = time.time() - start
            if time_in_mins:
                logger.info(
                    "{} took {}".format(func.__name__, timedelta(seconds=time_needed))
                )
            else:
                logger.info("{} took {:.4f}s".format(func.__name__, time_needed))
            if not get_time:
                return return_value
            return return_value, time_needed
        except Exception as exc:
            logger.exception("func {} raised exception {}".format(func.__name__, exc))
            raise exc

    return wrapper
