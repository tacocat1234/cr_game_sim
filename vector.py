import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, other):
        self.x += other.x
        self.y += other.y
        
    def subtract(self, other):
        self.x -= other.x
        self.y -= other.y
        
    def scale(self, scalar):
        self.x *= scalar
        self.y *= scalar

    def scaled(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

def distance(vec1, vec2):
    return math.sqrt((vec2.x - vec1.x) ** 2 + (vec2.y - vec1.y) ** 2)