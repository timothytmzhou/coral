from abc import ABC, abstractmethod
from namespace import main, Namespace


class Module:
    def __init__(self, statements, name, namespace=main):
        self.statements = statements
        self.name = name
        self.namespace = namespace

    def walk(self):
        for statement in self.statements:
            statement.exec(self.namespace)


class AST_Node(ABC):
    pass


class Statement(AST_Node):
    @abstractmethod
    def exec(self, namespace=main):
        pass


class Expression(AST_Node):
    @abstractmethod
    def eval(self):
        pass


class Assignment(Statement):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

    def exec(self, namespace=main):
        namespace[self.name] = self.expression.eval()


class Output(Statement):
    def __init__(self, expression):
        self.expression = expression

    def exec(self, namespace=main):
        print(self.expression.eval())


class ControlFlowElement(Statement):
    def __init__(self, statements):
        self.statements = statements

    def exec(self, namespace=main):
        for statement in self.statements:
            statement.exec(namespace)


class Conditional(ControlFlowElement):
    def __init__(self, condition, statements, next_node=None):
        super().__init__(statements)
        self.condition = condition
        self.next_node = next_node

    def exec(self, namespace=main):
        if self.condition.eval():
            super().exec(namespace)
        elif self.next_node is not None:
            self.next_node.exec(namespace)


class While(ControlFlowElement):
    def __init__(self, condition, statements):
        super().__init__(statements)
        self.condition = condition

    def exec(self, namespace=main):
        while self.condition.eval():
            super().exec(namespace)


class ObjectLookup(Expression):
    def __init__(self, name):
        self.name = name

    def eval(self, namespace=main):
        return namespace[self.name].value


class Call(Expression):
    def __init__(self, func):
        self.func = func

    def eval(self):
        f = self.func.eval()
        return f.call()


class Value(Expression):
    def __init__(self, obj):
        self.obj = obj

    def eval(self):
        return self.obj.value


class UnaryOperator(Expression):
    def __init__(self, func, child):
        self.func = func
        self.child = child

    def eval(self):
        return self.func(self.child.eval())


class BinaryOperator(Expression):
    def __init__(self, func, left, right):
        self.func = func
        self.left = left
        self.right = right

    def eval(self):
        return self.func(self.left.eval(), self.right.eval())
