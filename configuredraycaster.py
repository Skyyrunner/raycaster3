from scene import Scene
import objects
import euclid
from camera import Camera
import time
import sys

if __name__=="__main__":
    with open("config") as f:
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
    result = myScene.render(depth=depth, start=start, end=end, tofile=False)
    if not end:
        end = camera.imageh
    height = end - start
    endtime = time.clock()
    pixels = result.load()
    for y in range(height):
        print(pixels[0, y])
    print("Took %.2f seconds for rendering a %dx%d image." % (endtime - starttime,
        camera.imagew, height))