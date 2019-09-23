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



def gray(im):
    # Converts a numpy array (im) into a grayscale image for a pygame surface
    im = 255 * (im / im.max())
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
    return ret

# Get information from commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help="input TIFF file (you may add more than one)", action="append", required=True)
parser.add_argument('-f1', '--f1', help="determine which is the first frame in the ratio f1/f2", required=True)


args = parser.parse_args()

filelist = args.input

abs_i = int(args.f1)
file_i = int(args.f1)

try:
    image = tf.imread(filelist[0], key=0)
except:
    print("Couldn't open"+filelist[0])
    quit()
    


running = True

# Iterate through all files
#
# Make sure this works when spanning over multiple files!

t1 = time.time()

with tf.TiffWriter(filelist[0]+"_ratio.tif", bigtiff=True) as outtif: # Save ratio images into this file
    for file_index, filename in enumerate(filelist):
        
        # This code is horribly complicated and hard to understand.
        # There must be a better way to do this!
        while running:
            try:
                image_f1 = tf.imread(filename, key=file_i) # Read first frame
            except:
                try:
                    image_f1 = tf.imread(filelist[file_index+1], key=0)   
                    image_f2 = tf.imread(filelist[file_index+1], key=1)
                    outtif.save((image_f1/image_f2), compress=6, ) # Save ratio image
                    print("\rDividing frame",abs_i, "by", abs_i+1, end="") # Print status message
                    abs_i +=2
                    break
                except:
                    quit()
            try:
                image_f2 = tf.imread(filename, key=file_i+1) # Read next frame
            except:
                try:
                    image_f2 = tf.imread(filelist[file_index+1], key=0)                
                    outtif.save((image_f1/image_f2), compress=6, ) # Save ratio image
                    print("\rDividing frame",abs_i, "by", abs_i+1, end="") # Print status message
                    abs_i +=2
                    break
                except:
                    quit()

            outtif.save((image_f1/image_f2), compress=6, ) # Save ratio image
            print("\rDividing frame",abs_i, "by", abs_i+1, end="") # Print status message
            file_i+=2 # Iterate
            abs_i +=2
            
        file_i = 0 # Reset counter for every individual file
#pg.quit()

print(time.time()-t1)