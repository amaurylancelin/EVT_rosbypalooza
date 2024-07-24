# EVT_rossbypalooza
Project on EVT with Plasim data - focus on heatwaves and cold spells - Rossbypalooza 2024


## Data
Plasim data is stored in CISL NCAR cluster at : f"/glade/derecho/scratch/awikner/PLASIM/data/2000_year_sims_new/sim{sim_number}/{var}/".
There are 42 sim{sim_number} folders, each containing 2100 years of data (one file per year). The variables are stored in separate folders. 

In the data folder, there are 2 subfolders: 
- `ground_truth`: contains the ground truth data for the heatwaves and cold spells. It uses all sim data from sim0 to sim41.
- `train`: contains the data for fitting the GPD distribution. it uses only the sim0 data.