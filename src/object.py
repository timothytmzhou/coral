from namespace import Namespace
from textwrap import indent


class Func:
    def __init__(self, scope, name, args, statements):
        self.scope = scope
        self.name = name
        self.args = args
        self.arity = len(args)
        self.statements = statements

    def __str__(self):
        body = "args : {0},\n{1}".format(", ".join(self.args), self.statements)
        return "<Function> {0} {{\n{1}\n}}".format(self.name, indent(body, " " * 4))

    def __call__(self, *arg_vals):
        num_args = len(arg_vals)
        if num_args == self.arity:
            obj_dict = dict(zip(self.args, arg_vals))
            local_scope = Namespace(parent=self.scope, obj_dict=obj_dict)
            for statement in self.statements:
                statement.exec(local_scope)
        else:
            raise TypeError(
                "attempted to pass {0} arguments to function {1} of arity {2}".format(
                    num_args, self.name, self.arity
                )
            )
