author:  Tyler Ganter (tylergan@buffalo.edu)

SCRIPTS
----------------------------------------------------------------------------

    vid_Prep.sh
	-general information and tools for video preparation and accessing
		results
	-see file for details


DIRECTORIES
----------------------------------------------------------------------------

setup/
    The previously mentioned scripts are developed for convenience.  They
        use files in setup/

site/
    svxlabel.py
        -This file generates the webpages.  It uses the html files in templates/

static/

    videos/
        -This is where files/data that are needed/ready for the website
            are stored.
        -This folder holds a STRICT format.
        videos/ contains one subdirectory per algorithm used for segmentation and Output/:

        <algorithm>/ contains a folder per video it is ready for
            <video>/ contains:
                -all .png's of video, padded 5 digits and numbered starting at 00001.png
                -tree.json
                -data.json (only if data has been saved from client side)
                ONLY DIRECTORIES:
                -hierarchies, padded 2 and starting at 00
                    -each contains .png's numbered the same as the orginal video frames
                -labeled/  (only if svxl labeling is finished, from client side)
                    -contains .png's of labeled video
                    -update every time someone saves from Supervoxel Labeler

        Output/ (Similar to <algorithm>) contains:
                ONLY DIRECTORIES:
                -frames/
                    -original video frames
                -labeled/  (only if svxl labeling is finished, from client side)
                    -contains .png's of labeled video,
                    -update every time someone saves from Overlay/Post-Processing Labeler

        
