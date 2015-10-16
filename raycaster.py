from scene import Scene
import objects
import euclid
from camera import Camera
import time
import sys

if __name__=="__main__":
    #import rpdb2; rpdb2.start_embedded_debugger('1234')
    # do raycaster things
    objectlist = [objects.CollidableSphere(position=euclid.Point3(10.,0.,-5.), radius=3.,
                     color=(188, 198, 204), roughness=0.8),
                  objects.CollidableSphere(position=euclid.Point3(10.,0.,0.), radius=1.,
                     color=(0, 0, 255), roughness=1.0),
                  objects.CollidableSphere(position=euclid.Point3(1.,0.,0.), radius=.5,
                     color=(200, 200, 200), roughness=0.0, transparency=1.0, refractionIndex=1.1)]
    lights = [objects.Light(position=euclid.Point3(0.,0.,0.))]
    try:
        l = int(sys.argv[1])
    except:
        l = 256
    camera = Camera(imageDim=(l, l),focallength=2.0)
    myScene = Scene(camera=camera, objects=objectlist, lights=lights)
    starttime = time.clock()
    myScene.render(depth=2)
    endtime = time.clock()
    print("Took %.2f seconds for render." % (endtime - starttime))