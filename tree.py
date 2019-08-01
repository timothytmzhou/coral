from abc import ABC, abstractmethod
from namespace import *


class Module:
    def __init__(self, statements, name):
        self.statements = statements
        self.name = name


    def walk(self):
        for statement in self.statements:
            statement.exec()


class AST_Node(ABC):
    pass


class Statement(AST_Node):
    @abstractmethod
    def exec(self):
        pass


class Expression(AST_Node):
    @abstractmethod
    def eval(self):
        pass


# TODO: separate namespaces and scoping
class Assignment(Statement):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

    def exec(self):
        main.set_var(self.name, self.expression.eval())


class Output(Statement):
    def __init__(self, expression):
        self.expression = expression

    def exec(self):
        print(self.expression.eval())


class Primitive(Expression):
    cast = str

    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value

    def __str__(self):
        return str(self.value)


class Integer(Primitive):
    cast = int


class Float(Primitive):
    cast = float


class String(Primitive):
    pass


def UnaryOperator(Expression):
    def __init__(self, func, value):
        self.func = func
        self.value = value

    def eval(self):
        return self.func(self.value)


class BinaryOperator(Expression):
    def __init__(self, func, left, right):
        self.func = func
        self.left = left
        self.right = right

    def eval(self):
        return self.func(self.left.eval(), self.right.eval())
