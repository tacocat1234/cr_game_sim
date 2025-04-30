import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, other):
        self.x += other.x
        self.y += other.y

    def added(self, other):
        return Vector(self.x + other.x, self.y + other.y)
        
    def subtract(self, other):
        self.x -= other.x
        self.y -= other.y

    def subtracted(self, other):
        return Vector(self.x - other.x, self.y - other.y)
        
    def scale(self, scalar):
        self.x *= scalar
        self.y *= scalar

    def scaled(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def magnitude(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    
    def normalize(self):
        mg = self.magnitude()
        if (mg > 0):
            self.scale(1/mg)

    def rotated(self, degrees):
        angle_radians = math.radians(degrees)
        cos_theta = math.cos(angle_radians)
        sin_theta = math.sin(angle_radians)
        x_new = self.x * cos_theta - self.y * sin_theta
        y_new = self.x * sin_theta + self.y * cos_theta
        return Vector(x_new, y_new)

    def toString(self):
        return str(self.x) + ", " + str(self.y)

def distance(vec1, vec2):
    return math.sqrt((vec2.x - vec1.x) ** 2 + (vec2.y - vec1.y) ** 2)