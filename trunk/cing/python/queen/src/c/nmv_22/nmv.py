# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _nmv

def _swig_setattr(self,class_type,name,value):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    self.__dict__[name] = value

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types



initialize_matrix = _nmv.initialize_matrix

clear_matrix = _nmv.clear_matrix

free_memory = _nmv.free_memory

xplor_read = _nmv.xplor_read

uncertainty = _nmv.uncertainty

atom_uncertainty = _nmv.atom_uncertainty

total_uncertainty = _nmv.total_uncertainty

lower_bound = _nmv.lower_bound

upper_bound = _nmv.upper_bound
cvar = _nmv.cvar

