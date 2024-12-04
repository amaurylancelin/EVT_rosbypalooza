import numpy as np
import xarray as xr
import os
import argparse
import glob


def load_data_from_server(var_name):
    """Load ERA5 data from WHOI's server"""

    ## path to ERA5 dataset on WHOI's server
    ## to-do: use Pathlib
    era5_path = "/vortexfs1/share/cmip6/data/era5/reanalysis/single-levels/6hr"

    ## path to given variable
    var_path = os.path.join(era5_path, var_name)

    ## file pattern (each year of data is saved as individual file
    var_path_pattern = os.path.join(var_path, "*.nc")

    ## load data to file
    print(var_path_pattern)
    test = xr.open_dataset("/vortexfs1/share/cmip6/data/era5/reanalysis/single-levels/6hr/2m_temperature/1979-01_2m_temperature.nc")
    print("loaded test")
    data = xr.open_mfdataset(var_path_pattern, preprocess=preprocess, engine="netcdf4")

    return data


def trim_to_PNW(data):
    """Trim data to Pacific Northwest region
    as defined in Bartusek et al. (2021)"""

    ## lon/lat range
    lat_range = [60, 40]
    lon_range = [230, 250]

    return data.sel(latitude=slice(*lat_range), longitude=slice(*lon_range))


def landarea_weighted_mean(data, lsm=None):
    """Get landarea-weighted mean on regular lon-lat grid.
    Specifically, weight by cosine of latitude"""

    ## get cos(lat)
    cos_lat = np.cos(np.deg2rad(data.latitude))

    ## multiply by fraction of land, if land-sea mask is provided
    if lsm is None:
        weights = cos_lat

    else:
        weights = cos_lat * lsm

    return data.weighted(weights=weights).mean(["latitude", "longitude"])


def load_lsm_from_server():
    """Load land-sea mask (constant in time) from WHOI server"""

    ## filepath
    lsm_path = "/vortexfs1/share/cmip6/data/era5/reanalysis/single-levels/monthly-means/land_sea_mask/2022_land_sea_mask.nc"

    ## load the data
    lsm = xr.open_dataarray(lsm_path).isel(time=6, drop=True)

    return lsm

    # trim to Pac. NW
    return trim_to_PNW(lsm)


def preprocess(data):
    """pre-processing function to reduce data size"""

    ## load lsm
    lsm = load_lsm_from_server()

    ## trim LSM and data to Pac NW
    lsm_PNW = trim_to_PNW(lsm)
    data_PNW = trim_to_PNW(data)

    ## weighted mean
    data_PNW_mean = landarea_weighted_mean(data_PNW, lsm=lsm_PNW)

    return data_PNW_mean


def load_variable(var_name):
    """Load ERA5 data for given variable. Loads locally-saved
    data if available; otherwise downloads from WHOI's server"""

    ## local path for storing data
    ## To-do: use Pathlib
    local_data_path = f"../../data/{var_name}.nc"

    ## check if data is saved locally
    ## to-do: use Pathlib
    if os.path.isfile(local_data_path):
        print("Loading locally-saved data...")
        data = xr.open_dataset(var_name)

    else:
        print("Loading data from remote server...")
        data = load_data_from_server(var_name)

        ## save data locally for easier loading next time
        data.to_netcdf(local_data_path)

    print("Data load complete.")

    return data


if __name__ == "__main__":

    ## parse input: which variable to get?
    parser = argparse.ArgumentParser()
    parser.add_argument("--var_name")
    args = parser.parse_args()

    ## load the data
    data = load_variable(args.var_name)
