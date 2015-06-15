#!/usr/bin/python

import sys, json, Image, os
from os.path import join
from os import listdir
from glob import glob
from pprint import pprint

vid_name = sys.argv[1]
algo = sys.argv[2]
src = sys.argv[3]

path = '/projects/svxlabel/static/videos'
algo_path = os.path.join(path, algo, vid_name)
src_path = os.path.join(path, src, vid_name, 'labeled')
output_path = os.path.join(path, 'Output', vid_name)

#~ print algo_path
#~ print src_path
#~ print output_path

def to_idx(r,g,b):
    return "00%03d%03d%03d"%(r,g,b)

with open(join(output_path, 'data.json')) as f:
    json = json.loads(f.read())
    data = json['data']
    colors = json['colors']

svxl_imgs = sorted(glob(join(algo_path, '00', '*.png')))
src_imgs = sorted(glob(join(src_path, '*.png')))


for i in range(len(svxl_imgs)):
    outfile = join(output_path, "labeled/%05d.png") % (i+1)

    svxl_im = Image.open(svxl_imgs[i])
    src_im = Image.open(src_imgs[i])

    pix = svxl_im.load()
    src_pix = src_im.load()
    w,h = svxl_im.size
    for x in range(w):
        for y in range(h):
            idx = to_idx(*pix[x,y])
            if idx in data:
                color = colors[int(data[idx])]
                pix[x,y] = (color['r'], color['g'], color['b'])
            else:
                pix[x,y] = src_pix[x,y]

    svxl_im.save(outfile)
