# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 18:26:16 2019

@author: Gabriel
"""


import numpy as np
import tifffile as tf
import time
import argparse
from cv2 import VideoWriter, VideoWriter_fourcc



def gray(im):
    # Converts a numpy array (im) into a grayscale image for a pygame surface
    im = 255 * (im / im.max())
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
    return ret

# Get information from commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help="list of input TIFF files", action="append", required=True)
parser.add_argument('-d', '--downsampling', help="only show every n-th frame")
parser.add_argument('-s', '--startframe', help="select first frame for display")


args = parser.parse_args()

if(args.downsampling):
    d = int(args.downsampling)
else:
    d = 1
    
if(args.startframe):
    sf = int(args.startframe)
else:
    sf = 0   

filelist = args.input

try:
    image = tf.imread(filelist[0], key=0)
    frame_height, frame_width = image.shape
    print("Width:",frame_width, "Height:", frame_height)
except:
    print("Couldn't open"+filelist[0])
    quit()

# Initialize cv2

fourcc = VideoWriter_fourcc(*'H264')    
out = VideoWriter('c:/Temp/out.avi',fourcc, 10.0, (frame_width,frame_height))


                                                         
                                                         
running = True

# Iterate through all files
for filename in filelist:
    i = sf
        
    while running:
        try:
            print("\rConverting frame",i, end="") # Print status message
            image = tf.imread(filename, key=i)
            image = gray(image)
            print(image.shape, image.dtype)
            out.write(image)
            

            i=i+d
        except:
            print("\nEnd.")
            break

out.release()