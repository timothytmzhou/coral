from object import *


class Namespace(Object):
    def __init__(self, name):
        super().__init__(name)
        self.obj_dict = {}

    def get_var(self, name):
        if name in self.obj_dict:
            return self.obj_dict[name]
        else:
            raise LookupError

    def set_var(self, name, value):
        self.obj_dict[name] = Var(name, value)


main = Namespace("main")