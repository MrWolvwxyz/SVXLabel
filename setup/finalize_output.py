#!/usr/bin/python

# generates .png's from the supervoxel images and the associated data.json

import sys, json, Image
from os.path import join
from os import listdir
from glob import glob
from pprint import pprint

path = sys.argv[1]

def to_idx(r,g,b):
    return "00%03d%03d%03d"%(r,g,b)

with open(join(path, 'data.json')) as f:
    json = json.loads(f.read())
    data = json['data']
    colors = json['colors']

i=1
for imfile in sorted(glob(join(path, '00', '*.png'))):
    outfile = join(path, "labeled/%05d.png") % i
    i+=1

    im = Image.open(imfile)
    pix = im.load()
    w,h = im.size
    for x in range(w):
        for y in range(h):
            idx = to_idx(*pix[x,y])
            if idx in data:
                color = colors[int(data[idx])]
            else:
                color = colors[0]
            pix[x,y] = (color['r'], color['g'], color['b'])

    im.save(outfile)
