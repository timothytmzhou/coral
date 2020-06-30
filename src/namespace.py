class Namespace:
    def __init__(self, parent=None, obj_dict=None):
        self.parent = parent
        if obj_dict is not None:
            self.obj_dict = obj_dict
        else:
            self.obj_dict = {}

    def fetch(self, name):
        if name in self.obj_dict:
            return self.obj_dict[name]
        elif self.parent is not None:
            return self.parent.fetch(name)
        else:
            raise LookupError

    def push(self, name, value):
        self.obj_dict[name] = value
