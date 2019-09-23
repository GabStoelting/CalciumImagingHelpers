# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 18:26:16 2019

@author: Gabriel
"""


import numpy as np
import pygame as pg
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

# Get information from commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help="list of input TIFF files", \
                                        action="append", required=True)
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
filelist = natsorted(filelist)

try:
    image = tf.imread(filelist[0], key=0)
except:
    print("Couldn't open"+filelist[0])
    quit()

# Initialize pygame
pg.init()
myfont = pg.font.SysFont('Arial', 12)
screen = pg.display.set_mode(image.shape)
running = True

# Iterate through all files
for filename in filelist:
    i = sf

    while running:
        try:
            image = tf.imread(filename, key=i)
            image = gray(image)
            surf = pg.surfarray.make_surface(image)
            screen.blit(surf, (0,0))
            textsurface = myfont.render(filename, False, (255, 255, 0))
            screen.blit(textsurface, (0,0))
            textsurface = myfont.render(" frame "+str(i), False, (255, 255, 0))
            screen.blit(textsurface, (0,50))


            for ev in pg.event.get():
                if ev.type == pg.QUIT:
                    running = False
            pg.display.update()

            i=i+d
        except:
            break
pg.quit()
