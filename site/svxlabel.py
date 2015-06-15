from flask import Flask, request, json, render_template, g
from flask.ext.basicauth import BasicAuth
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image
from shutil import copy
import glob, os
import base64

app = Flask(__name__)
app.config.from_object("config")

basic_auth = BasicAuth(app)
class Videos():
    algo = None
    name = None
    width = None
    height = None
    length = None
    numhier = None

# Website Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Video Selection and Instructions
@app.route('/label')            # name of page
@basic_auth.required
def video_list():               # from this line to return, is preparing
    # Get algorithm choices     # variables to be passed into the template
    algo_directories = glob.glob('/projects/svxlabel/static/videos/*')
    
    uniqvideos = set()
    algos = {}
    
    for algo_path in algo_directories:
        (_, algo_name) = os.path.split(algo_path)
        
        # Get video choices
        directories = glob.glob(os.path.join(algo_path,'*'))

        videos = []
        for vid_path in directories:
            (_, vid_name) = os.path.split(vid_path)
            videos.append(vid_name)
            uniqvideos.add(vid_name)
                    
        algos[algo_name] = videos
    
    uniqvideos = sorted(list(uniqvideos))
    
    # html file is rendered as website with variable video_names
    return render_template('videos.html', video_names=uniqvideos)

# Options/Routing per video
@app.route('/select/<video>')
@basic_auth.required
def select(video=None):
    # Get algorithm choices
    algo_directories = glob.glob('/projects/svxlabel/static/videos/*')

    algos = {}
    
    for algo_path in algo_directories:
        (_, algo_name) = os.path.split(algo_path)
        
        algos[algo_name] = 0        # unavailable

        vid_path = os.path.join(algo_path,video)

        if os.path.exists(os.path.join(vid_path,'labeled')):
            algos[algo_name] = 3    # finished
        elif os.path.exists(os.path.join(vid_path,'data.json')):
            algos[algo_name] = 2    # started
        elif os.path.exists(vid_path):
            algos[algo_name] = 1    # get started!

    output = algos.pop('Output')
    
    return render_template('select.html', algoList=algos, vidName=video, output=output)

# Supervoxel Labeler Page
@app.route('/label/<algorithm>/<video>')
@basic_auth.required
def angular(algorithm=None, video=None):
    pngpaths = glob.glob(os.path.join('/projects/svxlabel/static/videos',algorithm,video,'*.png'))
    im = Image.open(pngpaths[0])
    w, h = im.size
    l = len(pngpaths)
    directories = glob.glob(os.path.join('/projects/svxlabel/static/videos',algorithm,video,'*/'))
    nh = len(directories) - 1
    
    for x in directories :
        if "labeled" in x :
            nh = -1
    
    viddata = Videos()
    viddata.algo = algorithm
    viddata.name = video
    viddata.width=w
    viddata.height=h
    viddata.length=l
    viddata.numhier=nh
    
    with open(os.path.join('/projects/svxlabel/static/videos',algorithm,video,'tree.json'), 'r') as file:
        svxtree = file.read()
        
    return render_template('angular.html', vid=viddata, svxtree=svxtree)

# Supervoxel Overlaying Page
@app.route('/over/<framesrc>/<algorithm>/<video>')
@basic_auth.required
def overlay(framesrc=None, algorithm=None, video=None):
    pngpaths = glob.glob(os.path.join('/projects/svxlabel/static/videos',algorithm,video,'*.png'))
    im = Image.open(pngpaths[0])
    w, h = im.size
    l = len(pngpaths)
    directories = glob.glob(os.path.join('/projects/svxlabel/static/videos',algorithm,video,'*/'))
    nh = len(directories) - 1
    
    for x in directories :
        if "labeled" in x :
            nh=nh-1
    
    viddata = Videos()
    viddata.algo = algorithm
    viddata.name = video
    viddata.width=w
    viddata.height=h
    viddata.length=l
    viddata.numhier=nh
    
    with open(os.path.join('/projects/svxlabel/static/videos',algorithm,video,'tree.json'), 'r') as file:
        svxtree = file.read()
        
    return render_template('overlay.html', vid=viddata, svxtree=svxtree, framesrc=framesrc)

# Post-Processing Page
@app.route('/post/<video>')
@basic_auth.required
def post(video=None):
    pngpaths = glob.glob(os.path.join('/projects/svxlabel/static/videos/Output',video,'frames/*.png'))
    im = Image.open(pngpaths[0])
    w, h = im.size
    l = len(pngpaths)
    directories = glob.glob(os.path.join('/projects/svxlabel/static/videos/Output/*/'))
    readyForPP = 0  # 0 = not ready for post-processing; -1 = ready
    
    for x in directories :
        if video in x :
            readyForPP = -1
    
    viddata = Videos()
    viddata.algo = 'Output'
    viddata.name = video
    viddata.width=w
    viddata.height=h
    viddata.length=l
    viddata.numhier=readyForPP
        
    return render_template('postProcessing.html', vid=viddata)

@app.route('/app')
def app_page():
    return render_template('app.html')

@app.route('/_view')
def view():
    # Display all saved data
    #~ cur = g.db.execute('select label from sessions')
    out = []
    #~ for label in cur:
        #~ out.append(label[0])
    return json.dumps(out)

@app.route('/_load', methods=['POST'])
def load():
    if request.method == 'POST':
        algo = request.json['algo']
        name = request.json['name']
        
        data_path = os.path.join('/projects/svxlabel/static/videos',algo,name,'data.json')
        try:
            with open(data_path) as data_file:
                data = data_file.read()
        except IOError:
            data = "none"
        
        return data

# Save request called from Supervoxel Labeler
@app.route('/_save', methods=['POST'])
def save():
    # Store the saved data
    if request.method == 'POST':
        data = request.json['data']
        colors = request.json['colors']
        finFlag = request.json['finishFlag']
        
        path = '/projects/svxlabel/static/videos/%s/%s/data.json' % (request.json['algo'], request.json['name'])
        with open(path, 'w') as file:
            file.write(json.dumps({'data': data, 'colors': colors}))
        
        # If finished flag is set:
        if finFlag==1:
            # create folder 'labeled'
            path = '/projects/svxlabel/static/videos/%s/%s/labeled' % (request.json['algo'], request.json['name'])
            os.mkdir(path)
            # generate output images in 'labeled'
            path = '/projects/svxlabel/static/videos/%s/%s' % (request.json['algo'], request.json['name'])
            os.system('/projects/svxlabel/setup/finalize_output.py %s' % path)
            return "Saved and finalized successfully"
        else:
            return "Saved successfully"

# Save request called from Supervoxel Overlayer
@app.route('/_saveOL', methods=['POST'])
def saveOL():
    # Store the saved data
    if request.method == 'POST':
        data = request.json['data']
        colors = request.json['colors']

        # Make directories in videos/Output/
        output_path = '/projects/svxlabel/static/videos/Output/%s' % request.json['name']
        if not(os.path.exists(output_path)):
            os.mkdir(output_path)
        
        frame_path = os.path.join( output_path, 'frames')
        if not(os.path.exists(frame_path)):
            os.mkdir(frame_path)
            # Copy frames to /frames
            frames = glob.glob(os.path.join('/projects/svxlabel/static/videos/',request.json['algo'],request.json['name'],'*.png'))
            for frame in frames:
                copy(frame, frame_path)
        
        label_path = os.path.join( output_path, 'labeled')
        if not(os.path.exists(label_path)):
            os.mkdir(label_path)
        
        # Save data.json file
        data_path = '/projects/svxlabel/static/videos/Output/%s/data.json' % request.json['name']
        with open(data_path, 'w') as file:
            file.write(json.dumps({'data': data, 'colors': colors}))
        
        os.system('/projects/svxlabel/setup/save_overlay.py %s %s %s' % (request.json['name'], request.json['algo'], request.json['framesrc']))

        if request.json['framesrc']=='Output':
            return "Saved successfully"
        else:
            return "Saved successfully.  Now change your frame source to 'Output' or go to Post-Processing"

# Save request called from Post-Processer
@app.route('/_savePP', methods=['POST'])
def savePP():
    # Store the saved data
    if request.method == 'POST':
        framenumber = request.json['frame'];
        data = request.json['data']
        
        meta, data = data.split(',', 1)
        img = base64.b64decode(data)
        
        path = '/projects/svxlabel/static/videos/%s/%s/labeled/%05d.png' % (request.json['algo'], request.json['name'], framenumber)
        with open(path, 'wb') as file:
            file.write(img)

        return "Saved successfully"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
