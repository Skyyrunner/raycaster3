from scene import Scene
import objects
import euclid
from camera import Camera

if __name__=="__main__":
    #import rpdb2; rpdb2.start_embedded_debugger('1234')
    # do raycaster things
    objectlist = [objects.CollidableSphere(position=euclid.Point3(10.,0.,-5.), radius=3., color=(255, 0, 255)),
                  objects.CollidableSphere(position=euclid.Point3(10.,0.,2.), radius=1., color=(0, 0, 255))]
    lights = [objects.Light(position=euclid.Point3(10.,0.,20.))]
    camera = Camera(imageDim=(256,256),focallength=2.0)
    myScene = Scene(camera=camera, objects=objectlist, lights=lights)
    myScene.render()