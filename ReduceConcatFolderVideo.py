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




import argparse
import os
import numpy as np
import tifffile as tf
from natsort import natsorted
from cv2 import VideoWriter, VideoWriter_fourcc
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
    compression_pairs = [(d, c//d) for d, c in zip(new_shape,
                                                   ndarray.shape)]
    flattened = [l for p in compression_pairs for l in p]
    ndarray = ndarray.reshape(flattened)
    for i in range(len(new_shape)):
        op = getattr(ndarray, operation)
        ndarray = op(-1*(i+1))
    return ndarray


def gray(im):
    # Converts a numpy array (im) into a grayscale RGB image
    # into a pygame surface
    im = 255 * (im / im.max())
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
    return ret


# Get information from commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help="input TIFF file directory",
                    required=True)
parser.add_argument('-b', '--binning', help="bxb pixels are averaged",
                    required=True)
parser.add_argument('-c', '--codec', help="set the four letter video codec")


args = parser.parse_args()

# Read directory and check if it really is one
directory = args.input
if(os.path.isdir(directory) is False):
    print(directory, "is not a directory.")
    quit()

# Import binning parameter
binning = int(args.binning)

# Check if a codec is specified, otherwise use "MP42"
if(args.codec):
    fourcc = VideoWriter_fourcc(*str(args.codec))
else:
    fourcc = VideoWriter_fourcc(*'MP42')


# Search through the specified directory
for subdir, dirs, files in os.walk(directory):
    filelist = []

    for file in files:
        # print os.path.join(subdir, file)
        filepath = subdir + os.sep + file

        if filepath.endswith(".tif") or filepath.endswith(".tiff"):
            filelist.append(filepath)  # append to filelist

    if(len(filelist) > 1):
        filelist = natsorted(filelist)  # sort if more than one
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

        # Save video into this file
        outavi = VideoWriter(filelist[0]+"_concat.avi", fourcc, 10.0,
                             (int(width/binning), int(height/binning)))

        # Save ratio images into this file
        with tf.TiffWriter(filelist[0]+"_concat.tif", bigtiff=True) as outtif:

            # Iterate through all files
            for filename in filelist:
                print(filename)
                i = 0

                while running:
                    try:
                        # Print status message
                        print("File {}/{}, converting frame {} from {} x {} px to \
                        {} x {} px".format(file_i, len(filelist), i, width,
                                           height, width/2, height/2))

                        image = tf.imread(filename, key=i)

                        # Reduce dimensions of images
                        image = bin_ndarray(image, new_shape=(int(height/binning),
                                                              int(width/binning)), operation="sum")
                        # Write frame to video
                        outavi.write(gray(image))

                        # Convert frame to 16bit integer for TIF
                        image = image.astype("uint16")
                        outtif.save(image, compress=6)

                        i = i+d

                    except IndexError:
                        print("\nReached end of file.")
                        break
                    except Exception as e:
                        print(e)
                        break

                file_i += 1

        outtif.close()
        outavi.release()
