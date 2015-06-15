#!/usr/bin/python

# This file creates a .json file with the structure of the segmentation
# hierarchies in order to find and label the level 0 labels from any
# level above

from PIL import Image
import os, glob, json, sys
import os.path as op
from pprint import pprint

tree = {}
def update_tree(pixel_list):
    """
    Takes a list of pixels, one from each hierarchy level, and all located at
    the same coordinate in their respective image. Modifies the tree such that
    supervoxels are parents of all supervoxels they overlap

    Assumes that the list is in order of hierarchy level, highest to lowest.
    """

    # Pointer into the tree structure
    tmptree = tree
    for pix in pixel_list:
        # Make sure the supervoxel is in the tree at the correct location
        if not pix in tmptree:
            tmptree[pix] = {}

        # Traverse down the tree
        tmptree = tmptree[pix]

# TODO: Make this a command line parameter
videopath = sys.argv[1]

directories = glob.glob(op.join(videopath,'*/'))
# Sort the directories, then reverse the list so it is highest to lowest
directories = sorted(directories)[::-1]

# Produce a list of lists of images, one for each hierarchy level
image_paths = []
for d in directories:
    paths = glob.glob(op.join(d, '*.png'))
    paths = sorted(paths)
    image_paths.append(paths)

# Transpose the lists so that it is a list of lists of hierarchy levels
image_paths = zip(*image_paths)

# For each frame of the video...
for i, l in enumerate(image_paths):
    print "Frame: ", i+1
    pprint(l)

    # Load the image from each hierarchy level, process it, store it in imlist
    imlist = []
    for h, path in enumerate(l):
        im = Image.open(path).convert('RGB')
        pixels = im.getdata()
        pixels = map(lambda p: "%02d%03d%03d%03d" % (len(directories)-1-h,p[0],p[1],p[2]), pixels)
        imlist.append(list(pixels))

    pixels = zip(*imlist)
    for pixlist in pixels:
        update_tree(pixlist)

with open(op.join(videopath, 'tree.json'), 'w') as file:
    file.write(json.dumps(tree))
