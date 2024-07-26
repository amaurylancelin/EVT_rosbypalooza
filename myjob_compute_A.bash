#!/bin/bash

var=tas
lat=48
lon=2
reduce=max

# Chicago - lat = 41, lon = -88
# China - lat=34.00, lon=109.00
# India - lat=27, lon=72
# NW US - lat=45, lon=-120
# Saudi - lat=25, lon=47
# Europe - lat=48, lon=2

for sim in 0
# for sim in 0 
do
    qsub -v var=$var,sim_number=$sim,reduce=$reduce,lat=$lat,lon=$lon myjob_compute_A.pbs
    echo $i
done