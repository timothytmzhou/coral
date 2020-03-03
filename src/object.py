class Object:
    cast = str

    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value

    def __str__(self):
        return str(self.value)


class Integer(Object):
    cast = int


class Float(Object):
    cast = float


class String(Object):
    pass
