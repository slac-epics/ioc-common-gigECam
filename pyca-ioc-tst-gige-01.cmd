#! /bin/bash

source /reg/g/pcds/setup/epicsenv-3.14.12.sh
source /reg/g/pcds/setup/pyca.sh

#cd ~pstoffel/py/work2
cd viewer-color
./prosilica1350.pyw --camera 13PS2 &
#cd ../viewer
cd ~pstoffel/py/work2
./prosilica1350.pyw --camera 13PS1 &
#python -m pdb ./prosilica1350.pyw --camera 13PS2
