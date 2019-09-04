class Object:
    def __init__(self, name):
        self.name = name


class Var(Object):
    def __init__(self, name, value):
        super().__init__(name)
        self.value = value
