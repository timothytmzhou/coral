from abc import ABC, abstractmethod
from object import Func
from namespace import Namespace


class Module:
    builtins = {
        "true": True,
        "false": False,
        "null": None,
        "print": print
    }

    def __init__(self, nodes, name):
        self.namespace = Namespace(obj_dict=Module.builtins)
        self.nodes = nodes
        self.name = name

    def walk(self):
        for node in self.nodes:
            if isinstance(node, Statement):
                node.exec(self.namespace)
            elif isinstance(node, Expression):
                node.eval(self.namespace)
            else:
                raise TypeError


class AST_Node(ABC):
    pass


class Statement(AST_Node):
    @abstractmethod
    def exec(self, namespace):
        pass


class Expression(AST_Node):
    @abstractmethod
    def eval(self, namespace):
        pass


class Assignment(Statement):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def exec(self, namespace):
        namespace.push(self.name, self.value.eval(namespace))


class FuncDef(Statement):
    def __init__(self, name, args, statements):
        self.name = name
        self.args = args
        self.statements = statements

    def exec(self, namespace):
        func = Func(scope=namespace, name=self.name, args=self.args,
                    statements=self.statements)
        namespace.push(self.name, func)


class Output(Statement):
    def __init__(self, expression):
        self.expression = expression

    def exec(self, namespace):
        print(self.expression.eval(namespace))


class Return(Statement, Exception):
    def __init__(self, expr):
        self.expr = expr

    def exec(self, namespace):
        self.val = self.expr.eval(namespace)
        raise self


class ControlFlowElement(Statement):
    def __init__(self, condition, statements):
        self.condition = condition
        self.statements = statements

    def exec(self, namespace):
        for statement in self.statements:
            statement.exec(namespace)


class Conditional(ControlFlowElement):
    def __init__(self, condition, statements, next_node=None):
        super().__init__(condition, statements)
        self.next_node = next_node

    def exec(self, namespace):
        if self.condition.eval(namespace):
            super().exec(namespace)
        elif self.next_node is not None:
            self.next_node.exec(namespace)


class While(ControlFlowElement):
    def __init__(self, condition, statements):
        super().__init__(condition, statements)

    def exec(self, namespace):
        while self.condition.eval(namespace):
            super().exec(namespace)


class Call(Expression):
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.arg_vals = args

    def eval(self, namespace):
        func = ObjectLookup(self.func_name).eval(namespace)
        try:
            func(*(arg.eval(namespace) for arg in self.arg_vals))
            return ObjectLookup("null")
        except Return as ret:
            return ret.val


class ObjectLookup(Expression):
    def __init__(self, name):
        self.name = name

    def eval(self, namespace):
        return namespace.fetch(self.name)


class Value(Expression):
    def __init__(self, value):
        self.value = value

    def eval(self, namespace):
        return self.value


class UnaryOperator(Expression):
    def __init__(self, func, value):
        self.func = func
        self.value = value

    def eval(self, namespace):
        return self.func(self.value)


class BinaryOperator(Expression):
    def __init__(self, func, left, right):
        self.func = func
        self.left = left
        self.right = right

    def eval(self, namespace):
        return self.func(self.left.eval(namespace), self.right.eval(namespace))
