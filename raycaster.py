from scene import Scene
import objects
import euclid
from camera import Camera
import time
import sys

if __name__=="__main__":
    #import rpdb2; rpdb2.start_embedded_debugger('1234')
    # do raycaster things
    objectlist = [objects.CollidableSphere(position=euclid.Point3(10.,0.,-15.), radius=3.,
                     color=(255, 215, 0), roughness=0.8),
                  objects.CollidableSphere(position=euclid.Point3(10.,0.,0.), radius=1.,
                     color=(0, 255, 0), roughness=0.99),
                  objects.CollidablePlane(origin=euclid.Point3(10.,0.,0.)
                    ,normal=euclid.Vector3(.5, 0.,1.),
                    roughness=0.8)]
    # objectlist = [
    #     objects.CollidablePlane(origin=euclid.Point3(10.,0.,0.),
    #         normal=euclid.Vector3(1.,1.,0.)),
    #     objects.CollidableSphere(position=euclid.Point3(3.,0.,0.),
    #         radius=1.0)
    # ]
    lights = [objects.Light(position=euclid.Point3(0.,0.,0.)),
    objects.Light(position=euclid.Point3(10.,0.,5.))]
    try:
        l = int(sys.argv[1])
    except:
        l = 256
    camera = Camera(imageDim=(l, l),focallength=2.0, screenDim=(8,8))
    myScene = Scene(camera=camera, objects=objectlist, lights=lights)
    myScene.skycolor = (90, 90, 255)
    starttime = time.clock()
    myScene.render(depth=3)
    endtime = time.clock()
    print("Took %.2f seconds for render." % (endtime - starttime))