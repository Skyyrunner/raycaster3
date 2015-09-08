from scene import Scene
import objects
import euclid
from camera import Camera

if __name__=="__main__":
    # do raycaster things
    objectlist = [objects.CollidableSphere(position=euclid.Point3(2.,0.,0.), color=(255, 0, 255))]
    lights = [objects.Light(position=euclid.Point3(-800.,1200.,0.))]
    lights = [objects.Light(position=euclid.Point3(-4., 5.,2.))]
    camera = Camera(imageDim=(256,256),focallength=2.0)
    myScene = Scene(camera=camera, objects=objectlist, lights=lights)
    myScene.render()