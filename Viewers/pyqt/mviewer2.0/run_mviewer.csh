#!/bin/tcsh
setenv LD_LIBRARY_PATH /reg/common/package/python/2.7.2/lib:/reg/common/package/qt/4.8.1/lib:/reg/g/pcds/package/epics/3.14/base/current/lib/linux-x86_64:/reg/g/pcds/package/epics/3.14/extensions/current/lib/linux-x86_64
setenv PATH /reg/g/pcds/package/epics/3.14/base/current/bin/linux-x86_64:/reg/g/pcds/package/epics/3.14/extensions/current/bin/linux-x86_64:/reg/common/package/python/2.7.2/bin:/reg/common/package/qt/4.8.1/bin:/bin:/usr/bin:$cwd
setenv EPICS_CA_MAX_ARRAY_BYTES 8388608
limit coredumpsize unlimited
setenv PYTHONPATH /reg/g/pcds/pds/pyca:/reg/g/pcds/controls
rehash

./mviewer.pyw $*

