import sys
import os
import pandas as pd
from tqdm import tqdm
from pathlib import Path

from src.utils import extract_data


# var = 'tas'
# sim_number = 0
# reduce = 'max'
# # Select lat and lon of Chicago
# latitude = float(34)
# longitude = float(109) % 360 # for longitudes take the value modulo 360

var = str(sys.argv[1]) # tas
sim_number = int(sys.argv[2]) # simulation number
reduce = str(sys.argv[3]) # max
latitude = float(sys.argv[4]) # latitude
longitude = float(sys.argv[5]) % 360# longitude

print(var, sim_number, reduce, latitude, longitude)

spatial_window_size = 2 # grid boxes

path = f"/glade/derecho/scratch/awikner/PLASIM/data/2000_year_sims_new/sim{sim_number}/"
if var == 'precip':
    path_files = path + '/prc'
else:
    path_files = path + f"{var}/"

if var == 'hus':
    filename_end = 'gaussian_postproc.nc'
else:
    filename_end = 'gaussian.nc'
    
files = [f for f in os.listdir(path_files) if f.endswith(filename_end)]

# Extracting data
all_data = []
for i in tqdm(range(11,len(files))):
  data=extract_data(path, i, var, latitude, longitude, reduce, spatial_window_size)
  all_data.extend(data)

# saving data
SAVE_DIR = f'data/ground_truth/sim{sim_number}/'
file_name = f'{var}_lat.{int(latitude)}_lon.{int(longitude)}_spatial.{spatial_window_size}_reduce.{reduce}.csv'
Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)

df = pd.DataFrame(all_data, columns=['Day', var])
df.to_csv(SAVE_DIR + file_name , index=False)