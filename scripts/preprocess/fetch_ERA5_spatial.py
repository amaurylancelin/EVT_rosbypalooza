import xarray as xr
import numpy as np
import os
import argparse
import time


def subset_for_PNW(data):
    """Get subset of reanalysis data for PNW"""

    ## list of variables to get
    vars_to_get = [
        "2m_temperature",
        "2m_dewpoint_temperature",
        "temperature",
        "specific_humidity",
        "surface_pressure",
        "geopotential",
        "volumetric_soil_water_layer_1",
        "volumetric_soil_water_layer_2",
        "mean_surface_latent_heat_flux",
        "mean_surface_net_long_wave_radiation_flux",
        "mean_surface_net_short_wave_radiation_flux",
        "mean_surface_sensible_heat_flux",
        "boundary_layer_height",
    ]

    ## subset for vars
    data = data[vars_to_get].sel(level=[500, 850])

    ## subset in lat/lon
    data = data.sel(latitude=slice(70,30), longitude=slice(200, 280))

    return data


def get_data_for_daterange(date_range):

    fp_hourly = "gs://weatherbench2/datasets/era5/1959-2023_01_10-full_37-1h-0p25deg-chunk-1.zarr"
    fp_6hourly = "gs://weatherbench2/datasets/era5/1959-2023_01_10-wb13-6h-1440x721_with_derived_variables.zarr"

    ## open dataset
    reanalysis = xr.open_zarr(
        fp_6hourly,
        consolidated=True,
        chunks={"time": 384},
    )

    ## subset for PNW region
    reanalysis = subset_for_PNW(reanalysis)

    ## subset in time
    reanalysis = reanalysis.sel(time=slice(*date_range))

    ## resample to 6-hourly (if using hourly data)
    # reanalysis = reanalysis.resample({"time": "6h"}).mean()

    return reanalysis


def get_clim(dayofyear):
    """Get climatology for given dayofyear array"""

    clim = xr.open_zarr(
        "gs://weatherbench2/datasets/era5-hourly-climatology/1990-2019_6h_1440x721.zarr",
        consolidated=True,
    )

    ## subset for PNW region
    clim = subset_for_PNW(clim)

    ## subset in time
    clim = clim.sel(dayofyear=dayofyear)

    return clim


def get_data_and_clim_for_daterange(date_range):
    """Get subset of data for given date range,
    plus the corresponding climatology"""

    ## get data
    data = get_data_for_daterange(date_range)

    ## get corresponding climatology
    dayofyear = np.unique(data.time.dt.dayofyear)
    clim = get_clim(dayofyear=dayofyear)

    return data, clim


def main():

    ## parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_date")
    parser.add_argument("--end_date")
    args = parser.parse_args()

    ## get data subset and climatology
    date_range = [args.start_date, args.end_date]
    data, clim = get_data_and_clim_for_daterange(date_range)

    ## save to files
    PNW_data_fp = os.path.join(os.environ["DATA_FP"], "PNW_ERA5")
    data_fp = os.path.join(
        PNW_data_fp, f"data_{date_range[0]}-{date_range[1]}.nc"
    )
    clim_fp = os.path.join(
        PNW_data_fp, f"clim_{date_range[0]}-{date_range[1]}.nc"
    )

 
    print("Saving data subset")
    t0 = time.time()
    data.to_netcdf(data_fp)
    tf = time.time()
    print(f"Elapsed time: {(tf-t0)/60:0f} minutes\n")

    print("Saving climatology.")
    t0 = time.time()
    clim.to_netcdf(clim_fp)
    tf = time.time()
    print(f"Elapsed time: {(tf-t0)/60:0f} minutes\n")

    return


if __name__ == "__main__":
    main()
