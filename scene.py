import camera
from PIL import Image
import euclid
import math

def clamp(m, x, M):
    if x < m:
        return m
    if x > M:
        return M
    return m

def dist(lineseg, point):
    L1 = abs(point - lineseg.p1)
    L2 = abs(point - lineseg.p2)
    return L1 if L1 < L2 else L2 # find the closer of the 2 points

def lerp(color1, color2, t):
    r1,g1,b1 = color1
    r2,g2,b2 = color2
    R = (1.0-t)*r1 + t*r2
    G = (1.0-t)*g1 + t*g2
    B = (1.0-t)*b1 + t*b2
    return (R,G,B)

def colorMultiply(rgb, n):
    r = rgb[0] * n
    g = rgb[1] * n
    b = rgb[1] * n
    return (r,g,b)

def colorSum(colors):
    R = G = B = 0.0
    for color in colors:
        R += color[0]
        G += color[1]
        B += color[2]
    return (R,G,B)

def colorFloor(color):
    r = int(color[0])
    g = int(color[1])
    b = int(color[2])
    return (r,g,b)

def weighedAverage(colors, weights):
    multcolors = []
    for i in range(len(colors)):
        multcolors.append(colorMultiply(colors[i], weights[i]))
    return colorFloor(colorSum(multcolors))


def floor(color):
    return (int(color[0]), int(color[1]), int(color[2]))

def closerPoint(lineseg, point):
    if isinstance(lineseg, euclid.Point3):
        return lineseg
    L1 = abs(point - lineseg.p1)
    L2 = abs(point - lineseg.p2)
    return lineseg.p1 if L1 < L2 else lineseg.p2 # find the closer of the 2 points

def furtherPoint(lineseg, point):
    if isinstance(lineseg, euclid.Point3):
        return lineseg
    L1 = abs(point - lineseg.p1)
    L2 = abs(point - lineseg.p2)
    return lineseg.p1 if L1 > L2 else lineseg.p2 # find the closer of the 2 points

class Scene:
    def __init__(self, camera=camera.Camera(), objects=[], lights=[]):
        self.camera = camera
        self.objects = objects
        self.lights = lights
        self.skycolor = (255,0,0)

    def findLightedColor(self, obj, point):
        truecolor = obj.getColor(point)
        # these two for highlights
        angles = []
        spectralAngles = []
        # this for brightness
        distances = []
        # this for intersection tests
        intersected = [] 

        # normal vector
        Vn = obj.normal(point).normalize()
        # line to viewer
        Vv = (point - self.camera.translation).normalize()

        # Try to draw a line to a light source
        for light in self.lights:
            ray = euclid.Ray3(point, light.position-point)
            canDoLight = True
            for thing in self.objects:
                inter = thing.intersect(ray)
                # if it's an intersection, no light!
                if inter and inter.length > 0.05:
                    if thing.getTransparency() > 0.0:
                        continue
                    else:
                        canDoLight = False
                        intersected.append(True)
                        break
            # spectral reflection stuff
            if canDoLight:
                intersected.append(False)

                N = obj.normal(point)
                N.normalize()
                dot = N.dot(ray.v.normalized())
                angles.append(dot)

                # find reflection vector & viewer vector angle
                Vl = (light.position - point)
                distances.append(len(Vl))
                Vl.normalize()
                # must rotate L around axis N x L, equal to angle.
                N_L_angle = math.acos(Vl.dot(N))
                axis = Vl.cross(N)
                rot = euclid.Quaternion.new_rotate_axis(N_L_angle*2, axis)
                Reflection = rot * Vl
                # get angle between viewer and reflection
                spectralAngles.append(Reflection.dot(Vv))

        shadowed = True
        for tf in intersected:
            shadowed &= tf

        if shadowed:
            return (0,0,0)
        
        angle = max(angles) # The greatest angle wins
        distance = min(distances) # smallest distance
        # but wait, there's more! Find the spectral lighting angle
        spectral = max(spectralAngles)
        # lighted color
        lightedcolor = truecolor #lerp((0,0,0), truecolor, 7 / distance**2)

        # If the material is more reflective, the highlight is smaller & more intense
        # but for now, if the angle is above a threshold make it white
        if spectral < -0.985:
            return lerp(lightedcolor, (255,255,255), abs((spectral+0.985)*100)**3)
        return lerp((0,0,0), lightedcolor, angle)

    def trace(self, ray, depth=0):
        hits = []
        for x in self.objects:
            inter = x.intersect(ray)
            if inter and inter.length > 0.05:
                    hits.append((inter,x))
        # Register the hit on the closest object
        if len(hits) > 0:
            if len(hits) == 2:
                1 == 1
            origin       = ray.p
            closestObj   = None
            closestPoint = None
            closestDist  = None
            for x,obj in hits:
                if not closestPoint:
                    closestObj = obj
                    closestPoint = closerPoint(x, origin)
                    closestDist = dist(x, origin)
                else:
                    distance = dist(x, origin)
                    if distance < closestDist:
                        closestDist = distance
                        closestPoint = closerPoint(x, origin)
                        closestObj = obj
            # With the closest object, get color or get secondary rays.
            diffuse = self.findLightedColor(closestObj, closestPoint)
            if depth <= 0:
                return diffuse
            # All secondary rays here
            # eg, reflection, refraction...
            # Sum up the colors, then return.

            """ Final color = (diffuseness + reflection) + refraction
                after all, diffuse colors are just really scattered reflections.
                transparent part is taken out first,
                then diffuse+reflection

            """
            reflected = (0,0,0)
            refracted = diffuse
            refracted_selfcolor = (0,0,0)
            
            transparency = closestObj.getTransparency()
            roughness    = (1 - transparency) * closestObj.getRoughness()
            reflection   = (1 - transparency) * closestObj.getReflectionIndex()
            
            normal = closestObj.normal(closestPoint)
            normal.normalize()

            if transparency > 0.0:
                # do refraction
                refractedray = self.refractRay(closestObj, closestPoint, normal, ray)
                refracted_selfcolor = colorMultiply(diffuse, 1 - transparency)
                if not refractedray:
                    refracted = diffuse
                else:
                    refracted = self.trace(refractedray, depth-1)
                refracted = weighedAverage([refracted, refracted_selfcolor],
                                           [transparency, 1-transparency])
                #...
                # sum colors, return true color
            if roughness < 1.0:
                ## do reflection
                #  rotate ray
                dotab = ray.v.dot(normal)
                rotatedray = ray.copy()
                rotatedray.v -= normal * dotab * 2
                rotatedray.p = closestPoint
                # trace!
                inter = closestObj.intersect(rotatedray)
                if inter:
                    direction = rotatedray.v.normalized()
                    rotatedray.p += direction * inter.length
                reflected = self.trace(rotatedray, depth-1)

            return weighedAverage([diffuse, reflected, refracted], 
                                  [roughness, reflection, transparency])
        # hit nothing
        return self.skycolor

    def refractRay(self, obj, intersect, normal, ray):
        cross = normal.cross(ray.v)
        ray.v.normalize()
        normal.normalize()
        cross.normalize()
        angleOfIncidence = math.acos(normal.cross(cross).dot(ray.v)) 
        n = obj.getRefractionIndex()     
        try:
            # first rotation is air to material.
            rotateBy = math.asin(math.sin(angleOfIncidence) / n)
            quat = euclid.Quaternion.new_rotate_axis(rotateBy, cross)
            ray = quat * ray
            ray.p = intersect
            # Next, find the exit point.
            lineseg = obj.intersect(ray)
            exit = furtherPoint(lineseg, ray.p)
            ray.p = exit.copy()
            # Rotate again, material to air.
            normal = obj.normal(ray.p)
            cross = normal.cross(ray.v)
            cross.normalize()
            angleOfIncidence = math.acos(normal.cross(cross).dot(ray.v))
            rotateBy = math.asin(math.sin(angleOfIncidence) * n)
            quat = euclid.Quaternion.new_rotate_axis(rotateBy, cross)
            ray = quat * ray
            ray.p = exit
            return ray
        except ValueError:
            return None

        

    def render(self, depth=1, filename="out/test.png"):
        img = Image.new('RGB', 
            (self.camera.imagew, self.camera.imageh), (0,0,255))
        pixels = img.load()
        for ray, x, y in self.camera.generateRays():
            color = self.trace(ray, depth)
            pixels[x,y] = floor(color)
        img.save(filename)