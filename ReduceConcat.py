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
from natsort import natsorted




def gray(im):
    # Converts a numpy array (im) into a grayscale image for a pygame surface
    im = 255 * (im / im.max())
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
    return ret

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
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help="input TIFF file (you may add more than one)", action="append", required=True)
parser.add_argument('-b', '--binning', help="bxb pixels are averaged", required=True)


args = parser.parse_args()

filelist = args.input
filelist = natsorted(filelist)

binning = int(args.binning)


try:
    image = tf.imread(filelist[0], key=0)
    height, width = image.shape
except:
    print("Couldn't open"+filelist[0])
    quit()
    
print(width, height)

running = True
d = 1

# Iterate through all files
#
# Make sure this works when spanning over multiple files!

with tf.TiffWriter(filelist[0]+"_concat.tif", bigtiff=True) as outtif: # Save ratio images into this file
    
    # Iterate through all files
    for filename in filelist:
        i = 0
            
        while running:
            try:
                print("\rConverting frame {} from {} x {} px to {} x {} px".format(i, width, height, width/2, height/2)) # Print status message
                image = tf.imread(filename, key=i)
                image = bin_ndarray(image, new_shape=(int(height/binning), int(width/binning)), operation="mean")             
                #image = gray(image)
                image = image.astype("uint16")
                outtif.save(image, compress=6)
                
    
                i=i+d
            except:
                print("\nEnd.")
                break

outtif.close()        
