from abc import ABC, abstractmethod
from namespace import main


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


class Assignment(Statement):
    def __init__(self, name, expression, namespace=main):
        self.name = name
        self.expression = expression
        self.namespace = namespace

    def exec(self):
        self.namespace.set_var(self.name, self.expression.eval())


class Output(Statement):
    def __init__(self, expression):
        self.expression = expression

    def exec(self):
        print(self.expression.eval())


class ControlFlowElement(Statement):
    def __init__(self, statements):
        self.statements = statements

    def exec(self):
        for statement in self.statements:
            statement.exec()


class Conditional(ControlFlowElement):
    def __init__(self, condition, statements, next_node=None):
        super().__init__(statements)
        self.condition = condition
        self.next_node = next_node

    def exec(self):
        if self.condition.eval():
            super().exec()
        elif self.next_node is not None:
            self.next_node.exec()


class ObjectLookup(Expression):
    def __init__(self, name):
        self.name = name

    def eval(self, namespace=main):
        return namespace.get_var(self.name).value


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


class UnaryOperator(Expression):
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
