import euclid

class Light:
    def __init__(self, position=euclid.Point3(0.,0.,0.), size=1.):
        self.position = position # a Point3
        self.size = size

class Collidable:
    def __init__(self, color=(255,255,0)):
        self.color = color
        self.reflectionIndex = 0.0
    
    def getColor(self, coords=None):
        return self.color

    def intersect(self, ray):
        raise BaseException("Must overload intersect() in class " + type(self).__name__)

    def normal(self, point):
        raise BaseException("Must overload normal() in class " +  type(self).__name__)

    def distance(self, ray):
        raise BaseException("Must overload distance() in class " + type(self).__name__)
        
    def __eq__(self, other):
        raise BaseException("Must overload __eq__() in class " + type(self).__name__)
        
    def __ne__(self, other):
        raise BaseException("Must overload __ne__() in class " + type(self).__name__)

class CollidableSphere(Collidable):
    def __init__(self, position=euclid.Point3(0.,0.,0.), color=(255,255,0), radius=1.):
        super().__init__(color=color)
        self.position = position
        self.radius = radius
        self.shape = euclid.Sphere(self.position, self.radius)

    def getColor(self, coords=None):
        return self.color

    def intersect(self, ray):
        return self.shape.intersect(ray)

    def distance(self, ray):
        return self.shape.distance(ray)

    def normal(self, point):
        return point - self.position

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        A = self.position == other.position
        B = self.radius == other.radius

        return A and B

    def __ne__(self, other):
        return not self.__eq__(other)
