#!/bin/bash

# Chicago - lat = 41, lon = -88
# China - lat=34.00, lon=109.00
# India - lat=27, lon=72
# NW US - lat=45, lon=-120
# Saudi - lat=25, lon=47
# Europe - lat=46, lon=6

sims=(41 42 43 44 45 46 47 48) 

var=tas
reduce=max

latitudes=(41 34 27 45 25)
longitudes=(-88 109 72 -120 47)

# Loop through each simulation and each set of latitude/longitude
for sim in "${sims[@]}"
do
    for i in "${!latitudes[@]}"
    do
        lat=${latitudes[$i]}
        lon=${longitudes[$i]}
        qsub -v var=$var,sim_number=$sim,reduce=$reduce,lat=$lat,lon=$lon myjob_compute_A.pbs
        echo "Submitted job with var=$var, lat=$lat, lon=$lon for sim=$sim"
    done
done

######### Europe #########
reduce=min

latitudes=(46)
longitudes=(6)

# Loop through each simulation and each set of latitude/longitude
for sim in "${sims[@]}"
do
    for i in "${!latitudes[@]}"
    do
        lat=${latitudes[$i]}
        lon=${longitudes[$i]}
        qsub -v var=$var,sim_number=$sim,reduce=$reduce,lat=$lat,lon=$lon myjob_compute_A.pbs
        echo "Submitted job with var=$var, lat=$lat, lon=$lon for sim=$sim"
    done
done

######### Precipitation #########

reduce=max

latitudes=(41 34 25)
longitudes=(-88 109 47)

for var in precip pl
do
for sim in "${sims[@]}"
do
    for i in "${!latitudes[@]}"
    do
        lat=${latitudes[$i]}
        lon=${longitudes[$i]}
        qsub -v var=$var,sim_number=$sim,reduce=$reduce,lat=$lat,lon=$lon myjob_compute_A.pbs
        echo "Submitted job with var=$var, lat=$lat, lon=$lon for sim=$sim"
    done
done
done
