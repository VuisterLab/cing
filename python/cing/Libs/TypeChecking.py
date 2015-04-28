"""

          ARIA -- Ambiguous Restraints for Iterative Assignment

                 A software for automated NOE assignment

                               Version 2.2


Copyright (C) Benjamin Bardiaux, Michael Habeck, Therese Malliavin,
              Wolfgang Rieping, and Michael Nilges

All rights reserved.


NO WARRANTY. This software package is provided 'as is' without warranty of
any kind, expressed or implied, including, but not limited to the implied
warranties of merchantability and fitness for a particular purpose or
a warranty of non-infringement.

Distribution of substantively modified versions of this module is
prohibited without the explicit permission of the copyright holders.
"""
from numpy.core.numeric import zeros as _zeros

FLOAT = 'FLOAT'
INT = 'INT'
STRING = 'STRING'
UNICODE = 'UNICODE'
DICT = 'DICT'
LIST = 'LIST'
TUPLE = 'TUPLE'
ARRAY = 'ARRAY'
NONE = 'NONE'
BOOL = 'BOOL'

TYPES = {type(0.): FLOAT,
         type(0): INT,
         type(''): STRING,
         type(u''): UNICODE,
         type({}): DICT,
         type([]): LIST,
         type(()): TUPLE,
         type(_zeros(0)): ARRAY,
         type(None): NONE,
         type(True): BOOL,
         type(False): BOOL}

for python_type, my_type in TYPES.items():
    TYPES[my_type] = python_type

class TypeChecker:

    def __init__(self, active = 1):

        self.check_type(active, INT)
        self.active = active

    def is_subclass(self, c, name):

        if c.__name__ == name:
            return 1

        for base in c.__bases__:
            return self.is_subclass(base, name)

        return 0

    def is_type(self, token, name):

        t = type(token)

        try:
            return TYPES[t] == name

        except:

            try:
#                token.__class__
                return self.is_subclass(token.__class__, name)
            except:
                pass

            if t == type(self.__class__):
                s = 'type-checking is not supported for classes. ' + \
                    'Argument is an instance of class "%s"'
                raise s % str(token)

            else:
                s = 'is_type: internal error.'
                raise StandardError, s

    def check_type(self, token, *names):

        ok = 0

        for name in names:
            ok = ok or self.is_type(token, name)

        if not ok:
            types = [TYPES.get(name, name) for name in names]

            if len(types) == 1:
                types = types[0]

            if type(token) == type(self):
                token_name = 'instance (%s)' % token.__class__.__name__
            else:
                token_name = type(token).__name__

            import inspect

            frame = inspect.currentframe().f_back.f_back
            code = frame.f_code
            func_name = code.co_name
            filename = code.co_filename
            lineno = frame.f_lineno

            descr = 'File "%s", line %d in %s: ' + \
                    '<%s> expected, <%s> given.'

            msg = descr % (filename, lineno, func_name, types, token_name)

            raise TypeError, msg

    def check_elements(self, seq, t):

        try:
            map(lambda e, t = t, s = self: s.check_type(e, t), seq)
        except TypeError, s:
            raise TypeError, s

    def __call__(self, x, *names):
        if self.active:
            self.check_type(x, *names)

check_type = TypeChecker(active=1)
del TypeChecker

is_type = check_type.is_type
check_elements = check_type.check_elements

check_int = lambda x: check_type(x, INT)
check_float = lambda x: check_type(x, FLOAT)
check_string = lambda x: check_type(x, STRING, UNICODE)
check_list = lambda x: check_type(x, LIST)
check_tuple = lambda x: check_type(x, TUPLE)
check_dict = lambda x: check_type(x, DICT)
check_array = lambda x: check_type(x, ARRAY)
check_file = lambda x: check_type(x, 'file')
