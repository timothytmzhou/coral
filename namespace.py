class Variable:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"{self.name} = {self.value}"


class Namespace:
    def __init__(self, name):
        self.name = name
        self.vars = []

    def get_var(self, name):
        for var in self.vars:
            if var.name == name:
                return var.value
        return None

    def set_var(self, name, value):
        for var in self.vars:
            if var.name == name:
                var.value = value
                break
        else:
            self.vars.append(Variable(name, value))


main = Namespace("main")