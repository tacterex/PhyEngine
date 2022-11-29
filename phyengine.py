from tkinter import Tk, Canvas
import tkinter as tk
import math

def simple_update():
    return 0

def cos(a):
    return math.cos(math.radians(a))

def sin(a):
    return math.sin(math.radians(a))

def sgn(a):
    return a/abs(a) if a != 0 else 0

class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def check_instance(fun):
        def wrap(self, other):
            if not isinstance(other, Vector):
                raise TypeError("types don't match")
            return fun(self, other)
        return wrap

    @check_instance
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    @check_instance
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector(self.x * other, self.y * other)

    def __truediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector(self.x / other, self.y / other)

    def __str__(self):
        return "Vector object with coords ({}, {})".format(self.x, self.y)

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __iter__(self):
        return iter((self.x, self.y))

    @property
    def unit(self):
        return self/abs(self)

    @classmethod
    def ZERO(cls):
        return cls(0, 0)

class BasicWindow(Tk):
    def __init__(self, sizex, sizey, ping = 30, scale = 10):
        super().__init__()
        self.geometry("{}x{}".format(sizex, sizey))
        self.x, self.y = sizex, sizey
        self.resizable(False, False)
        self.title("Experiment")
        self.Objects: list[DynamicObject] = list()
        self.ping = ping
        self.scale = scale

        self.update = simple_update

        self.canvas = Canvas(self)
        self.after(self.ping, lambda: self.raw_update_w())

    def start(self):
        self.canvas.pack(fill = tk.BOTH, expand = 1)
        self.mainloop()

    def InitObjects(self, *objects):
        self.Objects.extend(objects)

    @property
    def update(self):
        return self.raw_update_w

    @update.setter
    def update(self, fun):
        def wrap():
            fun()
            for obj in self.Objects:
                obj.raw_update_()
            self.after(self.ping, lambda: self.update())
        self.raw_update_w = wrap

class DynamicObjectBehaivour:
    def __init__(self, bounce_from_borders = False, fallable = False):
        self.boounce_from_borders = bounce_from_borders
        self.fallable = fallable

    @classmethod
    def STANDART(cls):
        return cls()

class DynamicObject:
    def __init__(self, window: BasicWindow, x, y, size, color = "red",
     collidable = True, behaivour: DynamicObjectBehaivour = DynamicObjectBehaivour.STANDART()):
        self.window = window
        self.canvas = window.canvas
        self.x, self.y, self.d = x, y, size
        self.color = color
        self.collidable = collidable
        self.behaivour = behaivour

        self.speed = Vector.ZERO()
        self.acceleration = Vector.ZERO()

        self.index = len(self.window.Objects) + 1
        self.update = simple_update

        self.object = self.canvas.create_oval(x - size/2, y - size/2, x + size/2, y + size/2, fill=color)
        window.InitObjects(self)

    def __eq__(self, other):
        return self.index == other.index

    def move(self, dx, dy):
        self.canvas.move(self.object, dx, dy)
        self.x += dx
        self.y += dy

    def stamp(self, color):
        self.canvas.create_oval(self.x - self.d/8, self.y - self.d/8,
         self.x + self.d/8, self.y + self.d/8, fill=color, width=0)

    @property
    def update(self):
        return self.raw_update_

    @property
    def dt(self):
        return self.window.ping / 1000

    @property
    def position(self):
        return Vector(self.x, self.y)
    
    @property
    def speed(self):
        return self.r_velocity

    @property
    def acceleration(self):
        return self.r_acceleration

    @position.setter
    def position(self, new_position: Vector):
        x, y = new_position
        self.canvas.move(self.object, x - self.x, y - self.y)
        self.x, self.y = x, y

    @speed.setter
    def speed(self, new_speed):
        self.r_velocity = new_speed

    @acceleration.setter
    def acceleration(self, new_acceleration: Vector):
        extra = Vector.ZERO()
        if self.behaivour.fallable:
            extra = Vector(0, 10)
        self.r_acceleration = new_acceleration + extra
    
    @update.setter
    def update(self, fun):
        def wrap():
            fun()
            self.move(*(self.r_velocity * self.dt * self.window.scale))
            self.r_velocity += self.r_acceleration * self.dt
            if self.behaivour.boounce_from_borders:
                if not (0 < self.x < self.window.x):
                    self.r_velocity.x *= -1
                if not (0 < self.y < self.window.y):
                    self.r_velocity.y *= -1
        self.raw_update_ = wrap

    @staticmethod
    def is_collision(first, second):
        if (not first.collidable) or (not second.collidable):
            return False
        return (first.x - second.x) ** 2 + (first.y - second.y) ** 2 <= ((first.d + second.d)**2)/4
