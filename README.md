Coral
=====
A programming language interpreter written from scratch in Python. Coral implmenets standard control flow (loops, functions, conditionals) and other basic operations like arithmetic and assignment.

# Parsing System
Coral implements its own parsing framework from scratch which abstracts away much of the messiness of parsing to create very readable code. Coral's grammar is fairly simple--the following is a (condensed) EBNF:
```
eof = ";";
parenthetical = "(" expr ")";

assignment = identifier , "=" , expr , eof;
loop = "while" , parenthetical , code_block;
conditional = "if" , parenthetical , code_block;
function = "func" , identifier , "=" , code_block;
return = "return" , expr , eof;
expression = expr , eof;

rule = assignment | conditional | function | expression;
code_block = "{" , { rule } , "}";

grammar = { rule };
```
In code, this is almost expressed verbatim as:
```
 patterns = {
        TokenSequence(TokenType.IDENTIFIER, "=") + eof: parse_assignment,
        TokenSequence("while") + parenthetical + code_block: parse_while,
        TokenSequence("if") + parenthetical + code_block: parse_if,
        TokenSequence("func", TokenType.IDENTIFIER) + TerminatingSequence("=") + code_block: parse_func,
        TokenSequence("return") + eof: parse_return,
        eof: parse_expr
    }
```
Where, `patterns` is a hashmap between `Pattern` objects and functions. `Patterns` do the heavy lifting, allowing for the functions themselves to be written in a highly declarative style. For instance, `parse_assignment` is more or less implemented as:
```
def parse_assignment(identifier, expr):
    return Assignment(identifier.value, parse_expr(expr))
```

# Examples
Hello world:
```
print "hello world";
```
Euclidean algorithm:
```
func gcd a b = {
    while (b) {
        tmp = b;
        b = a % b;
        a = tmp;
    }
    return a;
}

print (gcd 19323 2746);
```
Higher order functions:
```
func add_mul a b c = {
    return a + b * c;
}

func apply_1_2 f = {
    return f 1 2;
}

print (apply_1_2 add_mul);
```
