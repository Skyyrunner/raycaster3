from scene import Scene
import objects
import euclid
from camera import Camera
import time
import sys
import json

def parseconfig(config):
    data = json.loads(config)

# returns Image object
def dorender(conffilename, filename=None, start=0, end=None):
    with open(conffilename) as f:
        config = f.read().split("\n")
    objectlist = []
    lights = []
    camera = None
    myScene = None
    depth = 2
    start = 0
    end = None

    mode = None
    for thing in config:
        if thing == "objects":
            mode = "objects"
            continue
        elif thing == "lights":
            mode = "lights"
            continue
        elif thing == "other":
            mode = "other"
            continue
        else:
            if mode == "objects":
                objectlist.append(eval(thing))
            elif mode == "lights":
                lights.append(eval(thing))
            elif mode == "other":
                exec(thing)

    # do raycaster things
    starttime = time.clock()
    if filename:
        myScene.render(depth=depth, start=start, end=end, tofile=True, filename=filename)
    else:
        result = myScene.render(depth=depth, start=start, end=end, tofile=False)
    if not end:
        end = camera.imageh
    height = end - start
    endtime = time.clock()
    comment = ("Took %.2f seconds for rendering a %dx%d image." % (endtime - starttime,
        camera.imagew, height))
    return comment, result


if __name__=="__main__":
    dorender("config")