#!/bin/bash
docker run --rm -v  /volume1/homes/admin/stockAnalysis:/mnt -w /mnt --network eth0-macvlan stock:1 python $@
