import xarray as xr
import numpy as np
import time
import os


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


def preprocess(data, lsm):
    """pre-processing function to reduce data size"""

    ## trim LSM and data to Pac NW
    lsm_PNW = trim_to_PNW(lsm)
    data_PNW = trim_to_PNW(data)

    ## weighted mean
    data_PNW_mean = landarea_weighted_mean(data_PNW, lsm=lsm_PNW)

    ## resample to 6-hourly
    data_PNW_mean = data_PNW_mean.resample({"time":"6h"}).mean()

    return data_PNW_mean


def main():

    ## open dataset
    fp_6hourly = "gs://weatherbench2/datasets/era5/1959-2023_01_10-wb13-6h-1440x721_with_derived_variables.zarr"
    fp_hourly = "gs://weatherbench2/datasets/era5/1959-2023_01_10-full_37-1h-0p25deg-chunk-1.zarr"
    data = xr.open_zarr(fp_hourly, chunks={"time": 768})

    ## select relevant variables
    lsm = data["land_sea_mask"]
    data = data[["2m_temperature", "2m_dewpoint_temperature", "surface_pressure"]]

    ## do preprocessing
    data_prepped = preprocess(data, lsm=lsm)

    ## specify filepath for saving
    save_fp = os.path.join( os.environ["DATA_FP"], "PNW_ERA5", "era5_google_v2.nc")
    
    ## save to file
    start = time.time()
    data_prepped.to_netcdf(save_fp)
    end = time.time()

    ## print elapsed time
    elapsed_minutes = (end - start) / 60
    print(f"Elapsed time: {elapsed_minutes:.0f} minutes.")

    return


if __name__ == "__main__":
    main()
