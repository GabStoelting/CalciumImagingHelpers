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
import os
from natsort import natsorted


def gray(im):
    # Converts a numpy array (im) into a grayscale image for a pygame surface
    im = 255 * (im / im.max())
    w, h = im.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
    return ret


# Get information from commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help="directory with TIFF files", required=True)
parser.add_argument('-o', '--output', help="output TIFF file", required=True)
parser.add_argument('-d', '--downsampling', help="only show every n-th frame")
parser.add_argument('-s', '--startframe', help="select first frame")
parser.add_argument('-c', '--codec', help="set the four letter video codec")
parser.add_argument

args = parser.parse_args()

if(args.downsampling):
    d = int(args.downsampling)
else:
    d = 1

if(args.startframe):
    sf = int(args.startframe)
else:
    sf = 0

directory = args.input


# Initialize cv2

if(args.codec):
    fourcc = VideoWriter_fourcc(*str(args.codec))
else:
    fourcc = VideoWriter_fourcc(*'MP42')


running = True

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
        out = VideoWriter(filelist[0]+"_concat.avi", fourcc, 10.0, (width, height))

        running = True
        d = 1
        file_i = 1

        # Iterate through all files
        for filename in filelist:
            i = sf

            while running:
                try:
                    print("\rConverting frame", i, end="")  # Print status message
                    image = tf.imread(filename, key=i)
                    image = gray(image)
                    print(image.shape, image.dtype)
                    out.write(image)
                    i = i+d
                except IndexError:
                    print("Reached end of file")
                    i = 0
                    break
                except Exception as e:
                    print(e, "\nUnexpected Error. Quit.")
                    out.release()
                    quit()

out.release()
