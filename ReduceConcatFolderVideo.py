

import argparse
import os
import numpy as np
import tifffile as tf
from natsort import natsorted
from cv2 import VideoWriter, VideoWriter_fourcc
import time

def array_binning(a, n: int = 2):
    if n % 2 != 0:
        raise ValueError("The binning coefficient must be a multiple of 2.")
    for i in range(n // 2):
        a = a[::, ::2] + a[::, 1::2]
        a = a[::2, ::] + a[1::2, ::]
    return a


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
        runtime = [0, 0, 0, 0, 0]
        with tf.TiffWriter(filelist[0]+"_concat.tif", bigtiff=True) as outtif:

            # Iterate through all files
            for filename in filelist:
                t_start = time.time()
                print(filename)
                i = 0

                while running:
                    try:
                        t_0 = time.time()
                        image = tf.imread(filename, key=i)
                        t_1 = time.time()

                        # Reduce dimensions of images
                        image = array_binning(image, binning)
                        t_2 = time.time()

                        # Write frame to video
                        outavi.write(gray(image))
                        t_3 = time.time()

                        # Convert frame to 16bit integer for TIF
                        image = image.astype("uint16")
                        outtif.save(image, compress=0, photometric='minisblack')
                        t_4 = time.time()
                        i = i+d


                    except IndexError:
                        break
                    except Exception as e:
                        print(e)
                        break

                    # Print status message
                    print(f"File {file_i}/{len(filelist)}, converting frame {i}")
                    t_5 = time.time()
                    print(f"imread: {t_1-t_0}, binning: {t_2-t_1}, avi: {t_3-t_2}, tiff: {t_4-t_3}, total {t_5-t_0}")
                    runtime[0] += 1
                    runtime[1] += t_1-t_0
                    runtime[2] += t_2-t_1
                    runtime[3] += t_3-t_2
                    runtime[4] += t_4-t_3
                print(f"File total: {time.time()-t_start}")
                file_i += 1

print(runtime)
print(f"i: {runtime[0]} imread: {runtime[1]}, binning: {runtime[2]}, avi: {runtime[3]}, "
      f"tiff: {runtime[4]}, total {runtime[1]+runtime[2]+runtime[3]+runtime[4]}")

outtif.close()
outavi.release()
