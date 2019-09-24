# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 07:10:00 2019

@author: Gabriel
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 18:26:16 2019

@author: Gabriel
"""


import numpy as np
import tifffile as tf
import time
import argparse
import os
from natsort import natsorted

def bin_ndarray(ndarray, new_shape, operation='sum'):
    """
    Bins an ndarray in all axes based on the target shape, by summing or
        averaging.

    Number of output dimensions must match number of input dimensions and
        new axes must divide old ones.

    Example
    -------
    >>> m = np.arange(0,100,1).reshape((10,10))
    >>> n = bin_ndarray(m, new_shape=(5,5), operation='sum')
    >>> print(n)

    [[ 22  30  38  46  54]
     [102 110 118 126 134]
     [182 190 198 206 214]
     [262 270 278 286 294]
     [342 350 358 366 374]]

    """
    operation = operation.lower()
    if not operation in ['sum', 'mean']:
        raise ValueError("Operation not supported.")
    if ndarray.ndim != len(new_shape):
        raise ValueError("Shape mismatch: {} -> {}".format(ndarray.shape,
                                                           new_shape))
    compression_pairs = [(d, c//d) for d,c in zip(new_shape,
                                                  ndarray.shape)]
    flattened = [l for p in compression_pairs for l in p]
    ndarray = ndarray.reshape(flattened)
    for i in range(len(new_shape)):
        op = getattr(ndarray, operation)
        ndarray = op(-1*(i+1))
    return ndarray

# Get information from commandline arguments
#parser = argparse.ArgumentParser()
#parser.add_argument('-i', '--input', help="input TIFF file (you may add more \
#than one)", required=True)
#parser.add_argument('-b', '--binning', help="bxb pixels are averaged", \
#                    required=True)


#args = parser.parse_args()

#directory = args.input
directory = "G:\\Ca2+ Imaging\\02nov18 NNR Calbryte 520 AM"
binning = 2
#binning = int(args.binning)

for subdir, dirs, files in os.walk(directory):
    print("----")
    print(subdir, dirs)
    filelist = []

    for file in files:
        #print os.path.join(subdir, file)
        filepath = subdir + os.sep + file

        if filepath.endswith(".tif") or filepath.endswith(".tiff"):
            filelist.append(filepath) # append to filelist

    if(len(filelist)>1):
        filelist = natsorted(filelist) # sort if more than one
        print(filelist)
        try:
            image = tf.imread(filelist[0], key=0)
            height, width = image.shape
        except:
            print("Couldn't open"+filelist[0])
            quit()

        print(width, height)

        running = True
        d = 1
        file_i = 1
        # Iterate through all files
        #
        # Make sure this works when spanning over multiple files!

        # Save ratio images into this file
        with tf.TiffWriter(filelist[0]+"_concat.tif", bigtiff=True) as outtif:

            # Iterate through all files
            for filename in filelist:
                i = 0

                while running:
                    try:
                        # Print status message
                        print("\rFile {}/{}, converting frame {} from {} x {} px to \
                        {} x {} px".format(file_i, len(filelist), i, width, \
                        height, width/2, height/2), end="")

                        image = tf.imread(filename, key=i)

                        image = bin_ndarray(image, new_shape=(int(height/binning), \
                        int(width/binning)), operation="mean")

                        #image = gray(image)
                        image = image.astype("uint16")
                        outtif.save(image, compress=6)


                        i=i+d

                    except:
                        print("\nEnd.")
                        break
                file_i += 1

        outtif.close()
