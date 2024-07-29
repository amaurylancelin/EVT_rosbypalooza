import scipy.stats
import numpy as np
import pickle
import tqdm
import os.path

## initialize random number generator
rng = np.random.default_rng()


def fit_model(data, model_class):
    """Get model fitted to data. Returns scipy.rv_continuous object"""

    ## First, estimate parameters
    bounds = dict(c=[-1e1, 1e1], loc=[200, 400], scale=[1e-1, 1e1])
    params = scipy.stats.fit(dist=model_class, data=data, bounds=bounds).params

    ## instantiate random variable
    rv = model_class(*params)

    return rv


def get_return_levels(rv, return_periods=np.logspace(0.01, 3.5)):
    """get return value for given random variable at given return times"""

    return rv.isf(1 / return_periods), return_periods


def draw_sample(data, n=None):
    """draw random (bootstrap) sample from data.
    'n' is number of elements in given sample"""

    if n is None:
        n = len(data)

    return rng.choice(data, size=n, replace=True)


def load_return_period_bnds(data, model_class, save_fp, n_samples=1000, alpha=0.05):
    """load in or compute return period bounds"""

    if os.path.isfile(save_fp):

        ## open saved data
        with open(save_fp, "rb") as file:
            bounds = pickle.load(file)

        lb = bounds["lb"]
        ub = bounds["ub"]

    else:

        ## compute bounds
        lb, ub = compute_return_period_bnds(
            data, model_class=model_class, n_samples=n_samples, alpha=alpha
        )

        ## save to file
        with open(save_fp, "wb") as file:
            pickle.dump({"lb": lb, "ub": ub}, file)

    return lb, ub


def compute_return_period_bnds(data, model_class, n_samples=1000, alpha=0.05):
    """get bounds for return period using bootstrap sampling"""

    ## empty list to hold result
    return_levels_samples = []

    ## loop through number of samples
    for _ in tqdm.tqdm(range(n_samples)):

        ## fit model on bootstrapped sample
        model = fit_model(draw_sample(data), model_class=model_class)

        ## compute return period
        return_levels_samples.append(get_return_levels(model)[0])

    ## convert to array and compute bounds
    return_levels_samples = np.stack(return_levels_samples, axis=0)
    lb, ub = np.quantile(return_levels_samples, axis=0, q=[alpha / 2, 1 - alpha / 2])

    return lb, ub


def get_empirical_pdf(data, bin_edges=None):
    """function to get empirical PDF (normalized histogram)"""

    ## Set bin_edges if unspecified
    if bin_edges is None:
        bin_edges = np.linspace(np.floor(data.min()), np.ceil(data.max()), 20)

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
