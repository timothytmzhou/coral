class Var:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Namespace:
    def __init__(self, obj_dict=None, parent_namespaces=None):
        if obj_dict is None:
            obj_dict = {}
        self.obj_dict = obj_dict
        self.parent_namespace = parent_namespaces

    def extend(self, vars):
        """
        adds multiple vars into obj_dict
        :param vars: dict of form {name: value}
        """
        for name, value in vars.items():
            self[name] = value

    def __getitem__(self, item):
        if item in self.obj_dict:
            return self.obj_dict[item]
        elif self.parent_namespace is not None:
            return self.parent_namespace[item]
        else:
            raise LookupError

    def __setitem__(self, key, value):
        assert isinstance(key, str)
        self.obj_dict[key] = Var(key, value)


main = Namespace({
    "true": Var("true", True),
    "false": Var("false", False),
    "null": Var("null", None)
})
