#!/bin/bash
source /reg/g/pcds/setup/epicsenv-3.14.12.sh

# Reset ROI5 for BinnedImage binning
caput ${CAM}:ROI5:Name				BinnedImage
caput ${CAM}:ROI5:NDArrayPort		CAM
caput ${CAM}:ROI5:MinCallbackTime	0.2
caput ${CAM}:ROI5:Scale				64.0
caput ${CAM}:ROI5:BinX				2
caput ${CAM}:ROI5:BinY				2
caput ${CAM}:ROI5:EnableX			1
caput ${CAM}:ROI5:EnableY			1
caput ${CAM}:ROI5:EnableScale		1
caput ${CAM}:ROI5:EnableCallbacks	1

# Reset BinnedImage plugin
caput ${CAM}:BinnedImage:NDArrayPort		ROI5
caput ${CAM}:BinnedImage:MinCallbackTime	0.5
caput ${CAM}:BinnedImage:EnableCallbacks	1

# Reset ROI6 for Thumbnail binning
caput ${CAM}:ROI6:Name				Thumbnail
caput ${CAM}:ROI6:NDArrayPort		CAM
caput ${CAM}:ROI6:MinCallbackTime	0.2
caput ${CAM}:ROI6:Scale				256.0
caput ${CAM}:ROI6:BinX				4
caput ${CAM}:ROI6:BinY				4
caput ${CAM}:ROI6:EnableX			1
caput ${CAM}:ROI6:EnableY			1
caput ${CAM}:ROI6:EnableScale		1
caput ${CAM}:ROI6:EnableCallbacks	1

# Reset BinnedImage plugin
caput ${CAM}:Thumbnail:NDArrayPort		ROI6
caput ${CAM}:Thumbnail:MinCallbackTime	0.5
caput ${CAM}:Thumbnail:EnableCallbacks	1
