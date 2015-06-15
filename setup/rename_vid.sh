#!/bin/bash

# renames .png's to (00001.png, 00002.png, ....00NNN.png)

cd $1

# prevents images from being overwritten if they contain %05d.png
# format already (i.e. if index starts at 00000.png)
k=1
for i in *.png
do
    newname=$(printf frame%05d.png $k)
    mv $i $newname
    (( k += 1 ))
done

# correctly renames images
k=1
for i in *.png
do
    newname=$(printf %05d.png $k)
    mv $i $newname
    (( k += 1 ))
done
