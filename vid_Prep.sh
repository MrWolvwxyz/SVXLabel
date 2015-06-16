#!/bin/bash

# author:  Tyler Ganter (tylergan@buffalo.edu)

# This file is not to be run!
# This file provides information and example code that can be placed in
# a new file or directly in a terminal as needed.

echo "Read this file!"
exit

##### Storage
# ----------------------------------------------------------------------
#
### library/
#   Although it is not required to place anything here, the library is
#    where all source videos, images, svxl images and output labels can
#    be found.
#   These videos are broken into blocks based on the time they were
#    added:
#       annotation_videos_1, annotation_videos_2...
#   The library can be found at:
#       /media/mindseye/library
#       /projects/library       (shortcut)
#
### vdeos/
#   For a video to be labeled on the web it needs to be in a specific
#    folder and hold a strict format.  All source frames for the website
#    are found in this folder.
#   The videos can be found at:
#       /media/mindseye/videos
#       /projects/svxlabel/static/videos         (shortcut)
#       /projects/svxlabel-dev/static/videos     (shortcut)
#
### chatsubo
#   A backup of both the library and svxlabel(including videos/) can be
#    found on chatsubo.


##### Video Preparation
# ----------------------------------------------------------------------
#
### videos/
#   As stated before, videos/ holds a strict format.  It contains a
#    folder for every algorithm available and one specifically for
#    outputs ( Output/ ).
#   If a new algorithm is to be added simply add a new directory with
#    its name.  To remove an algorithm entirely, remove the folder with
#    its name.
#
#   example contents:  GAtech  GBH  Output  SWA  TSP
#
### <algorithm>
#   Within each algorithm folder, there is a folder for each video
#    that that algorithm is ready to label.
#   It is not necessary for a video to be available for all possible
#    algorithms.
#   example contents:  Avatar  Dog_Play  Hugs  Puppy_Piano
#
### <video>
#   To be ready for labeling on the site the video folder mush contain:
#~~1.The original frames (png format)
#       These can be copied from library/.../<video>/frames
#
#       Or generated using:
ffmpeg -i <video>.avi .../<video>/%05d.png
#       If the files are not .png's they can be converted using:
mogrify -format png *.ppm
#       The frames should be padded with 5 zeros starting at 00001.png
#
#~~2.The segmentation frames in hierarchal folders (png format)
#       There should be a folder for each hierarchy padded with 2 zeros
#        and starting at 00/.  Each folder should contain a png image
#        respective to each original frame.
#       If in the library, these frames can be found in
#        <video>/<algorithm>_output
#
#       To copy only every 7th level starting at 00/ run the following:
cd library/.../<video>/<algorithm>_output
for f in $(echo */ | sed 's/ /\n/g' | awk '(NR+6) % 7 == 0')
do
  cp -R $f videos/.../<video>
done
#       N can substitute 7 and (N-1) can substitute 6
#
#       To rename these directories run:
cd videos/.../<video>
j=1
for i in */
do
if [ $i != "00/" ]; then
  newname=$(printf %02d $j)
  mv $i $newname
  (( j += 1 ))
else
  newname=$i
fi
done
#
#~~3.A json file called tree.json
#       This file contains the information about how the hierarchy
#        levels lay over one another.
#
#       To create this file call:
cd /projects/svxlabel/setup
./create_tree.py ../static/videos/<algorithm>/<video>
#
#~~4.Finally, the permissions need to be correct in order to work.
#       These commands can be run on the specific video folder or, more,
#        easily, on all of videos/ to ensure everything is correct.
chmod -R +r <video>
find . -type d -exec chmod +x {} \;
sudo chgrp -R www-data <video>


##### Video Set Preparation Shortcut
#-----------------------------------------------------------------------
#
#   To make things easier when adding a full set of videos create a
#    script using the following code.  This code will loop through every
#    video in the folder, passing the name of the video as a variable.
source="/projects/library/annotation_videos_"$1/

IN=$(ls $source)
VIDS=()

while IFS=' ' read -ra OUT; do
  for i in "${OUT[@]}"; do
    VIDS+=($i)
  done
done <<< "$IN"

echo "Number of videos:"${#VIDS[@]}
echo $source

    # For each VID in source
for vid in "${VIDS[@]}"; do
  echo "Now processing:" $vid
    # Video Preparation calls
    # go here! Use $vid for the
    # video name.
done

#   As a result, run:
yourFile.sh N
#   to repeat all preparation steps for video set N.


##### The Labeling Process
#-----------------------------------------------------------------------
#
### data.json
#   The first time the 'Save' button is clicked from the supervoxel
#    labeler a 'data.json' file is created in the video's folder.  This
#    file contains information about the labels: color and name
#    and information about the labels, which hold the format:
#    "00RGB" "N" (three digits for each of R,G,B) which represents the
#    supervoxel color at level 00.  N is what label is associated with
#    the supervoxel.
#   Everytime 'Save' is clicked this is updated this file is updated.
#
### labeled/
#   When 'Finished' is clicked, data.json is updated and also, a folder
#    called labeled/ is created and label images are created in it.  The
#    images are created using the supervoxel frames and data.json.
#   These frames can be created outside of the site by calling:
cd /projects/svxlabel/setup
./finalize_output.py ../static/videos/<algorithm>/<video>
#
### Output/
#   As stated before, as well as a folder for each algorithm, there is a
#    directory, videos/Output.
#   When moving to the Supervoxel Overlaying step, the first time the
#    only load options will be from the algorithms that have been
#    'Finished'.  Clicking 'Save Output' from the overlay page will, the
#    first time, do four things:
#       1. create a folder Output/<video>
#       2. create a frames/ folder in <video>/ and copy the frames to it
#       3. create a data.json, only the labels (color and name) are
#           important
#       4. create a folder labeled/ and create label frames in it
#   Each following call will update data.json and the frames in labeled/
#   These frames can be created in the same way that they can be for the
#    initial Supervoxel Labeling:
cd /projects/svxlabel/setup
./save_overlay.py <video> <algorithm> <framesrc>
#   This function takes:
#       data.json from Output/<video>
#       supervoxel frames from <algorithm>/<video>
#       already labeled frames from <framesrc>/<video>
#   <framesrc> can be and algorithm or Output/
#   The only difference between finalize_output.py and save_overlay.py
#    is that in save_overlay.py, if a supervoxel is not labeled, the
#    pixel color is taken from <framesrc> rather than set to white.


##### The Results
#-----------------------------------------------------------------------
#
#   The final labels will be found in Output/<video>/labeled/.
#   While in this location, at any point the frames can be modified with
#    Supervoxel Overlaying or Post-Processing.
#   It would be smart to have a Google Doc to know when a user is
#    finished labeling.
#   To make sure you have the ability to modify the results as needed,
#    call:
chown -R <username> videos/
#   When a video labeling is finished move Output/<video>/labeled/* and
#    Output/<video>/data.json to an finished labels location in library/
#   To prepare a video for another user to label:
rm -R videos/Output/<video>
rm videos/*/<video>/data.json
rm -R videos/*/<video>/labeled/


##### General Video Formatting
#-----------------------------------------------------------------------
#
#   In library/ there is a <video>/<video>.mp4 (same name) that is
#    resized and is the video used for the site.  The not-.mp4-format
#    video or .mp4 with a different name is the original.
#   To resize the video call:
ffmpeg -i <video>.avi -vf scale=480:-1 -acodec copy -b 80000k <video>.mp4
#   To convert frames to a video:
ffmpeg -f image2 -i frames/%05d.png -vcodec mpeg4 -b 80000k <video>.mp4


##### Algorithm Specific
#-----------------------------------------------------------------------
#
### GAtech
#   Go to: http://videosegmentation.com/ to use the segment converter.
#   Under Segmentation Options:
#       Oversegmentation minimum size = 1% will break up the supervoxels
#        at the lowest level.
#       Min number of regions = 25 (or more) will stop segmentation
#        before excessive merging.
#   This converter will output a file: <video>_segment.pb
#
#   There is a segment converter available at:
/projects/Gatech_videosegmentation_v2/videosegmentation_utilities/mysegment_converter/
#   From this directory call:
./segment_converter .../<video>_segment.pb --bitmap_color gatech_output
#    to create an output at gatech_output/.  Then move this output
#    folder to library/.../<video>/
#   Then copy and rename a select number of segmentation levels to
#    videos/ using the code described in Video Preparation above.

### GBH
#   The following line of code will generate the results in library/.
#   As with GAtech, use the code described in Video Preparation above to
#    copy selective levels to the site.
./gbh 5 200 100 0.5 20 library/.../<video>/frames library/.../<video>/gbh_output

### SWA
#   To create a configuration file for SWA run the following:
path="<respective_path>/<video>"
numFrames=$(ls -1 frames/*.png | wc -l)

echo "InputSequence="$path"frames/%05d.png" >> config_file.txt
echo "Frames="$numFrames"-"$numFrames >> config_file.txt
echo "NumOfLayers=12" >> config_file.txt
echo "MaxStCubeSize=300" >> config_file.txt
echo "VizLayer=6-12" >> config_file.txt
echo "VizFileName="$path"SWA/swa_output" >> config_file.txt

#   In this code <respective_path> is the path to the video from the
#    location of the swa executable, (or where swa is being executed
#    from).
#   Make sure that MaxStCubeSize > numFrames!

### TSP
#   Code to run TSP can be found in:
/projects/Chang/code
#   Run:
TSP_output(<N>,'<video>')
#    where <N> is the annotation_videos_N number
#   Run a .m file with:
TSP_output(1,'<video1>')
TSP_output(1,'<video2>')
TSP_output(N,'<video3>')
...
#    to run many videos at the same time.
#   Modify TSP_output.m, first comment out 'Generate images' and 'Move
#    output to associated video folder' to prepare the videos. (Takes a
#    long time).
#   Then uncomment those, and comment out 'Infer the TSPs' to quickly
#    generate segmentation frames and move them to the appropriate
#    folders.
