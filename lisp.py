import math
import operator as op
from collections import ChainMap as Environment

Symbol = str           # A Lisp Symbol is implemented as a Python str
List = list            # A Lisp List   is implemented as a Python list
Number = (int, float)  # A Lisp Number is implemented as a Python int or float


class Procedure(object):
    "A user-defined Scheme procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args):
        env = Environment(dict(zip(self.parms, args)), self.env)
        return eval(self.body, env)

# Global Environment


def standard_env():
    "An environment with some Scheme standard procedures."
    env = {}
    env.update(vars(math))  # sin, cos, sqrt, pi, ...
    env.update({
        '+': (op.add, True),
        '-': (op.sub, True),
        '*': (op.mul, True),
        '/': (op.truediv, True),
        '>': (op.gt, True),
        '<': (op.lt, True),
        '>=': (op.ge, True),
        '<=': (op.le, True),
        '=': (op.eq, True),
        'abs': (abs, True),
        'append': (op.add, True),
        'apply': (lambda proc, args: proc(*args), True),
        'begin': (lambda *x: x[-1], True),
        'first': (lambda x: x[0], True),
        'rest': (lambda x: x[1:], True),
        'cons': (lambda x, y: [x] + y, True),
        'eq?': (    op.is_, True),
        'equal?': ( op.eq, True),
        'length': ( len, True),
        'list': (lambda *x: list(x), True),
        'list?': (lambda x: isinstance(x, list), True),
        'map': (lambda *args: list(map(*args)), True),
        'max': (max, True),
        'min': (min, True),
        'not': (op.not_, True),
        'null?': (lambda x: x == [], True),
        'number?': (lambda x: isinstance(x, Number), True),
        'procedure?': (callable, True),
        'round': (round, True),
        'symbol?': (lambda x: isinstance(x, Symbol), True)
    })
    return env


global_env = standard_env()

# Parsing: parse, tokenize, and read_from_tokens


def parse(program):
    "Read a Scheme expression from a string."
    tokens = tokenize(program)
    token = tokens.pop(0)
    L = []
    L.append(token)
    L.append(read_from_tokens(tokens))
    return L


def tokenize(s):
    "Convert a string into a list of tokens."
    token_list = []
    split_comma_list = s.replace(' ', '').split(',')
    print("split comma list:", split_comma_list)
    for part in split_comma_list:
        token_list += part.replace('(', '%f(') \
                          .replace('(', ' ( ') \
                          .replace(')', ' ) ') \
                          .split()
    token_list = list(filter(lambda x: x != '%f', token_list))
    print("token list:", token_list)
    return token_list


def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # remove trailing ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)

# Interaction: A REPL


def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        val = eval(parse(input(prompt)))
        if val is not None:
            print(lispstr(val))


def lisp_2_str(exp):
    "Convert a Python object back into a Lisp-readable string."
    if isinstance(exp, List):
        return str(exp[0]) + ' ' + lispstr(exp[1:][0])
    else:
        return str(exp)


def lispstr(exp):
    "Convert a Python object back into a Lisp-readable string."
    if isinstance(exp, List):
       return '(' + ', '.join(map(lispstr, exp)) + ')'
    else:
        return str(exp)

# eval

def isfunc(x, env):
    print("into isfunc: ", x)
    if x.endswith('%f'):
        print ("is function: ", x)
        return True
    else:
        print ("not a function")
        return False

def func_has_args(x):
    if len(x) > 0:
        return isinstance(x[0], List)
    else:
        return False

def eval(x, env=global_env):
    print (">>> into eval, x = ", x)
    "Evaluate an expression in an environment."
    if isinstance(x, List) and isfunc(x[0], env):
        func = env[x[0]][0]
        print ("function :", func)
        args = get_args(x[1:][0], env)
        print ("function: {0}, args : {1}".format(func, args))
        return func(*args)
    elif isinstance(x, Symbol):
        # A Symbol - variable reference - look it up in env
        print ("is instance: ", x)
        s =  env[x]
        print ("env is: ", x)
        return s
    elif not isinstance(x, List):
        # Not a Symbol or a list - constant literal - unchanged
        print ("is not instance: ", x)
        return x
    elif isinstance(x, List) and x[0] == 'quote':
        # it's a list but not a function - first element is a parameter
        print ("is quote: ", x)
        (_, exp) = x
        if not isinstance(exp, List):
            return exp
        elif isinstance( exp, List) and \
           (len(exp) > 1 or (len(exp) == 1 and any(isinstance(i,List) for i in exp))):
            return exp
        else:
            return exp[0]
    elif isinstance(x, List):
        # it's a list but not a function - first element is a parameter
        print ("it's a list: ", x)
        return eval(x[0], env)
    else:
        print("   >>> ERROR <<<")
        print ("what is this: ", x)
        return x

def get_args(arg_list, env=global_env):
    print("into get_args:", arg_list)
    args = []
    while len(arg_list) > 0:
        if isfunc(arg_list[0], env):
            func = [arg_list.pop(0)]
            if func_has_args(arg_list):
                args.append(eval(func +  [arg_list.pop(0)], env))
            else:
                args.append(eval(func, env))
        else:
            args.append(eval(arg_list.pop(0), env))
    return args





#    elif x[0] == 'if':             # (if test conseq alt)
#        print ("is if: ", x)
#        (_, test, conseq, alt) = x
#        exp = (conseq if eval(test, env) else alt)
#        return eval(exp, env)
#    elif x[0] == 'define':         # (define var exp)
#        print ("is define: ", x)
#        (_, var, exp) = x
#        env[var] = eval(exp, env)
#    elif x[0] == 'lambda':         # (lambda (var...) body)
#        print ("is lambda: ", x)
#        (_, parms, body) = x
#        return Procedure(parms, body, env)
