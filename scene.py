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
    L1 = len(point - lineseg.p1)
    L2 = len(point - lineseg.p2)
    return L1 if L1 < L2 else L2 # find the closer of the 2 points

def lerp(color1, color2, t):
    r1,g1,b1 = color1
    r2,g2,b2 = color2
    R = (1.0-t)*r1 + t*r2
    G = (1.0-t)*g1 + t*g2
    B = (1.0-t)*b1 + t*b2
    return (R,G,B)

def floor(color):
    return (int(color[0]), int(color[1]), int(color[2]))

def closerPoint(lineseg, point):
    L1 = len(point - lineseg.p1)
    L2 = len(point - lineseg.p2)
    return lineseg.p1 if L1 < L2 else lineseg.p2 # find the closer of the 2 points

class Scene:
    def __init__(self, camera=camera.Camera(), objects=[], lights=[]):
        self.camera = camera
        self.objects = objects
        self.lights = lights
        self.skycolor = (255,0,0)

    def findLightedColor(self, obj, point):
        truecolor = obj.getColor(point)
        angles = []
        spectralAngles = []
        distances = []

        # normal vector
        Vn = obj.normal(point).normalize()

        # line to viewer
        Vv = (point - self.camera.translation).normalize()

        # Try to draw a line to a light source
        for light in self.lights:
            ray = euclid.Ray3(point, light.position)
            canDoLight = True
            for thing in self.objects:
                # skip self
                if thing == obj:
                    continue

                inter = obj.intersect(ray)
                # if it's an intersection, no light!
                if inter:
                    canDoLight = False
                    break
            # determine the lighted color.
            if canDoLight:
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

        # The greatest angle wins
        angle = max(angles)

        distance = min(distances) # smallest distance

        # but wait, there's more! Find the spectral lighting angle
        spectral = max(spectralAngles)


        # lighted color
        lightedcolor = lerp((0,0,0), truecolor, 7 / distance**2)

        # If the material is more reflective, the highlight is smaller & more intense
        # but for now, if the angle is above a threshold make it white
        if spectral < -0.985: 
            return lerp(lightedcolor, (255,255,255), abs((spectral+0.985)*100)**3)

        return lerp((0,0,0), lightedcolor, angle)

    def trace(self, ray, depth=0, previous=None):
        hits = []
        for x in self.objects:
            # skip self
            if x == previous:
                continue
            # otherwise get intersect
            inter = x.intersect(ray)
            if inter != None:
                hits.append((inter,x))
        # Register the hit on the closest object
        if len(hits) > 0:
            origin = ray.p
            closestObj = None
            closestPoint = None
            closestDist = None
            for x,obj in hits:
                if not closestPoint:
                    closestObj = obj
                    closestPoint = x
                    closestDist = dist(x, origin)
                else:
                    distance = dist(x, origin)
                    if distance < closestDist:
                        closestDist = distance
                        closestPoint = x
                        closest = obj
            # With the closest object, get color or get secondary rays.
            if depth <= 0:
                return self.findLightedColor(closestObj, closerPoint(closestPoint, origin))
            # All secondary rays here
            # eg, reflection, refraction...
            # Sum up the colors, then return.
            color = (255,255,0)
            return color
        # hit nothing
        return self.skycolor

                           


    def render(self, filename="out/test.png"):
        img = Image.new('RGB', 
            (self.camera.imagew, self.camera.imageh), (0,0,255))
        pixels = img.load()
        for ray, x, y in self.camera.generateRays():
            color = self.trace(ray)
            pixels[x,y] = floor(color)
        img.save(filename)

