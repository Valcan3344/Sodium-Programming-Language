from sys import argv, stdout
from time import time
start = time()

SEPAEATORS = {
    '(', ')', '[', ']', '{', '}', ',', '\n', ' ', '+', '-', '*', '/', '%', '^', '='
}
DIGITS = {
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'
}

# Keywords
KW_PRINT   = 'print'
KW_VAR     = 'store'
KW_EXECUTE = 'execute'
KW_DEF     = 'define'
KW_IF      = 'if'
KW_WHEN    = 'when'
KW_END     = 'end'


INSTRUCTIONS = {
    KW_PRINT,
    KW_VAR,
    KW_EXECUTE,
    KW_DEF,
    KW_IF,
    KW_WHEN,
    KW_END
}

# Operators
OPERATORS = {
    'is',
    'isnt',
    '<',
    '>'
}


# Tokens
TT_INSTRUCTION = 'INSTRUCTION'
TT_OPERATORS   = 'OPERATORS'
TT_STRING      = 'STRING'
TT_NUM         = 'NUMBER'
TT_IDENTIFYER  = 'IDENTIFYER'
TT_SEPARATOR   = 'SEPARATOR'

variables = {}
functions = {}

def typeof(string=''):
    if string == '': return None
    if string[0] == '"' and string[-1] == '"':
        return 'string'

    for i in string:
        if i not in DIGITS:
            return None
    if string.count('.') <= 1:
        return 'number'


def precedence(op):
    if op == '+' or op == '-':
        return 1
    if op == '*' or op == '/':
        return 2
    return 0

def applyOp(a, b, op):
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/': return a // b
    if op == 'is' and a == b or op == 'isnt' and a != b or op == '<' and a < b or op == '>' and a > b:
        return 'true'
    return 'false'

def evaluate(tokens, types, temp_var={}):
    values = []
    ops = []

    for i in range(len(tokens)):
        if tokens[i] == '(':
            ops.append(tokens[i])

        elif tokens[i].isdigit():
            values.append(int(tokens[i]))

        elif types[i] == TT_IDENTIFYER:
            try:
                var_value = str(variables[tokens[i]])
            except:
                var_value = str(temp_var[tokens[i]])
            values.append(int(var_value) if var_value.isdigit() else var_value)

        elif tokens[i][0] == '"' and tokens[i][-1] == '"':
            values.append(tokens[i][1: -1])


        elif tokens[i] == ')':
            while len(ops) != 0 and ops[-1] != '(':
                val2 = values.pop()
                val1 = values.pop()
                op = ops.pop()
                values.append(applyOp(val1, val2, op))

            ops.pop()

        # Current tok is an operator
        else:
            while len(ops) != 0 and precedence(ops[-1]) >= precedence(tokens[i]):
                val2 = values.pop()
                val1 = values.pop()
                op = ops.pop()
                values.append(applyOp(val1, val2, op))

            ops.append(tokens[i])


    while len(ops) != 0:
        val2 = values.pop()
        val1 = values.pop()
        op = ops.pop()
        values.append(applyOp(val1, val2, op))

    return values[-1]

class Instruction:
    def __init__(self, name='', connectors=[]):
        self.name = name
        self.connectors = connectors

    def __repr__(self):
        return f'{self.name}'


##################################################################################################

def read_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as src:
        content = src.readlines()
        content[-1] += '\n'
        return content

def tokenize(stmt):
    current_tok = ''
    quote_count = 0
    tokens = []
    for i in stmt:

        if i == '"': quote_count += 1
        if i == '#': break

        if i in SEPAEATORS and quote_count % 2 == 0:
            if current_tok != '':
                tokens.append(current_tok)
            if i != ' ' and i != '\n':
                tokens.append(i)

            current_tok = ''
        else: current_tok += i

    return tokens

def parse(tokens):
    types = []
    for i in tokens:
        if i in INSTRUCTIONS:
            types.append(TT_INSTRUCTION)
        elif i in OPERATORS:
            types.append(TT_OPERATORS)
        elif i in SEPAEATORS:
            types.append(TT_SEPARATOR)
        elif typeof(i) == 'string':
            types.append(TT_STRING)
        elif typeof(i) == 'number':
            types.append(TT_NUM)
        else:
            types.append(TT_IDENTIFYER)

    return types


class Instruction:
    def __init__(self, name, connectors=[], stmts=[]):
        self.name = name
        self.connectors = connectors
        self.stmts = stmts

    def __repr__(self):
        return f'{self.name}'

class Interpreter:
    def __init__(self):
        self.current_cl = 0
        self.executing_cl = 0

        self.in_function = False
        self.func_name = ""
        self.stmts_in_func = []
        self.connectors = []


    def PRINT(self, val):
        if '\\n' in val:
            for i in val.split("\\n")[:-1]:
                stdout.write(f'{i}\n')
            return
        stdout.write(f'{val}')

    def DEFINE(self, name, connectors):
        self.current_cl += 1
        self.in_function = True
        self.func_name = name
        self.connectors = connectors
        functions.update({self.func_name : None})

    def interpret(self, tokens, types, temp_var={}):
        if not types or types[0] != TT_IDENTIFYER and types[0] != TT_INSTRUCTION: return

        if tokens[0] == KW_END:
            if self.executing_cl == self.current_cl: self.executing_cl -= 1
            self.current_cl -= 1

            functions[self.func_name] = Instruction(self.func_name, self.connectors, self.stmts_in_func)
            self.in_function = False
            self.func_name = ''
            self.connectors = []
            return

        if self.in_function:
            self.stmts_in_func.append([tokens, types])

        if self.current_cl != self.executing_cl:
            return

        # When calling a function
        if types[0] == TT_IDENTIFYER:
            "INSTRUCTION ARGS"
            instruc = functions[tokens[0]]
            ARGS = tokens[1:]
            tp_var = {}
            for i in range(len(ARGS)):
                tp_var.update({instruc.connectors[i]:ARGS[i]})

            for i in instruc.stmts:
                self.interpret(i[0], i[1], tp_var)
            return

        if tokens[0] == KW_PRINT:
            "print EXPR"
            EXPR = str(evaluate(tokens[1:], types[1:], temp_var))
            self.PRINT(EXPR)
            return

        if tokens[0] == KW_VAR:
            "store EXPR VAR"
            EXPR = tokens[1:len(tokens) - 1]
            VAR = tokens[-1]
            variables.update({VAR: evaluate(EXPR, types[1:len(tokens) - 1], temp_var)})
            return

        if tokens[0] == KW_DEF:
            "define NAME CONNECTORS"
            self.DEFINE(name=tokens[1], connectors=tokens[2:])
            return

        if tokens[0] == KW_IF:
            "if CONDI"
            CONDI = evaluate(tokens[1:], types[1:], temp_var)
            self.current_cl += 1
            if CONDI == 'true':
                self.executing_cl += 1


def main():
    current_line = 0
    text = read_file(file_name=argv[-1])

    interp = Interpreter()

    for stmt in text:
        current_line += 1
        tokens = tokenize(stmt)
        try:
            interp.interpret(tokens, parse(tokens))
        except Exception as e:
            stdout.write(f"\nException in line {current_line}: {e}\n")



if __name__ == '__main__':
    main()
    stdout.write(f'\nExecution time: {time() - start} sec')
