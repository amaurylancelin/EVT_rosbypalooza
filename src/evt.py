import scipy.stats
import numpy as np
import pickle
from tqdm import tqdm
import os.path

# ## initialize random number generator
rng = np.random.default_rng()


def fit_model(data, model_class, bounds):
    """Get model fitted to data. Returns scipy.rv_continuous object. 
    Bounds should be a dictionary with keys 'c', 'loc', 'scale'"""

    ## First, estimate parameters
    # bounds = dict(c=c if c is not None else [-1e1, 1e1],
    #               loc=loc if loc is not None else [200, 400],
    #               scale=scale if scale is not None else [1e-1, 1e1])
    #
    params = scipy.stats.fit(dist=model_class, data=data, bounds=bounds).params

    ## instantiate random variable
    rv = model_class(*params)

    return rv


def get_return_levels(rv, return_periods=np.logspace(0.01, 5)):
    """get return value for given random variable at given return times"""

    return rv.isf(1 / return_periods), return_periods


def draw_sample(data, n=None):
    """draw random (bootstrap) sample from data.
    'n' is number of elements in given sample"""

    if n is None:
        n = len(data)

    return rng.choice(data, size=n, replace=True)


def load_return_period_bnds(data, model_class, save_fp, bounds, n_samples=1000, alpha=0.05, MC=False, **kwargs):
    """load in or compute return period bounds"""
    if os.path.isfile(save_fp):

        ## open saved data
        with open(save_fp, "rb") as file:
            bounds = pickle.load(file)

        lb = bounds["lb"]
        ub = bounds["ub"]
    else:
        ## compute bounds
        if not MC: 
            lb, ub = compute_return_period_bnds(
            data, model_class=model_class, n_samples=n_samples, alpha=alpha, bounds=bounds)
            ## save to file
            with open(save_fp, "wb") as file:
                pickle.dump({"lb": lb, "ub": ub}, file)
        else:
            mean, median, lb, ub = compute_MC_return_period_bnds(data, model_class=model_class, bounds=bounds, alpha=alpha, **kwargs)
            ## save to file
            with open(save_fp, "wb") as file:
                pickle.dump({"mean": mean, "median": median, "lb": lb, "ub": ub}, file)

    if MC:
        return mean, median, lb, ub
    else: 
        return lb, ub
    



def compute_return_period_bnds(data, model_class, bounds, n_samples=1000, alpha=0.05):
    """get bounds for return period using bootstrap sampling"""

    ## empty list to hold result
    return_levels_samples = []

    ## loop through number of samples
    for _ in tqdm(range(n_samples)):

        ## fit model on bootstrapped sample
        if model_class == scipy.stats.norm:
            model = scipy.stats.norm(loc=data.mean(), scale=data.std())
        model = fit_model(draw_sample(data), model_class=model_class, bounds=bounds)

        ## compute return period
        return_levels_samples.append(get_return_levels(model)[0])

    ## convert to array and compute bounds
    return_levels_samples = np.stack(return_levels_samples, axis=0)
    lb, ub = np.quantile(return_levels_samples, axis=0, q=[alpha / 2, 1 - alpha / 2])

    return lb, ub

def compute_MC_return_period_bnds(full_data, model_class, bounds, alpha=0.05, n_train=80, n_mc=10):
    """get bounds for return period using Monte Carlo sampling"""
    ## empty list to hold result
    return_levels_samples = []
    for i in tqdm(range(n_mc)):
        # split data into training and testing
        train_data = draw_sample(full_data, n_train)
        # fit model on
        model = fit_model(train_data, model_class=model_class, bounds=bounds)
        # compute return period
        return_levels_samples.append(get_return_levels(model)[0])

    ## convert to array and compute bounds
    return_levels_samples = np.stack(return_levels_samples, axis=0)
    lb, ub = np.quantile(return_levels_samples, axis=0, q=[alpha / 2, 1 - alpha / 2])
    # return mean, median, lb, ub
    return np.mean(return_levels_samples, axis=0), np.median(return_levels_samples, axis=0), lb, ub
        


def get_empirical_pdf(data, bin_edges=None):
    """function to get empirical PDF (normalized histogram)"""

    ## Set bin_edges if unspecified
    if bin_edges is None:
        print(f"Number of bins not specified. Using square root rule. {np.sqrt(len(data)).astype(int)}")
        bin_edges = np.linspace(np.floor(data.min()), np.ceil(data.max()), np.sqrt(len(data)).astype(int))

    ## make histogram
    counts, _ = np.histogram(data, bins=bin_edges)

    # normalize histogram
    bin_width = bin_edges[1:] - bin_edges[:-1]
    pdf_empirical = counts / (counts * bin_width).sum()

    return pdf_empirical, bin_edges


def get_empirical_return_period(X):
    """Get empirical return period. Returns 'tr_empirical' and 'Xr_empirical';
    both are used to plot empirical return period."""

    # Empirical return period
    Xr_empirical = np.sort(X)
    n = len(X)
    m = np.arange(1, n + 1)
    cdf_empirical = m / (n + 1)
    tr_empirical = 1 / (1 - cdf_empirical)

    return tr_empirical, Xr_empirical


def compute_MC_return_value(full_data, model_class, bounds, n_train=80, n_mc=10, return_periods=100):
    """Compute the return value at a target return period using Monte Carlo simulation
    """
    ## empty list to hold result
    return_levels_samples = []
    for i in tqdm(range(n_mc)):
        # split data into training and testing
        train_data = draw_sample(full_data, n_train)
        # fit model on
        if model_class == scipy.stats.norm:
            model = scipy.stats.norm(loc=train_data.mean(), scale=train_data.std())
        else:
            model = fit_model(train_data, model_class=model_class, bounds=bounds)
        # compute return period
        return_levels_samples.append(get_return_levels(model, return_periods=return_periods)[0])

    ## convert to array and compute bounds
    return_levels_samples = np.stack(return_levels_samples, axis=0)
    return return_levels_samples

def get_target_return_value(X_test, target_return_period):
    """Interpolate the return value at a target return period with the 
    empirical return periods of the whole ground truth"""
    
    t_test_r_empirical, X_test_r_empirical = get_empirical_return_period(X_test)

    index_target_rv = np.argmin(np.abs(t_test_r_empirical - target_return_period))
    if t_test_r_empirical[index_target_rv] < target_return_period:
        index_target_rv += 1
    target_rv = np.mean(X_test_r_empirical[index_target_rv-1:index_target_rv+1])
    return target_rv, index_target_rv