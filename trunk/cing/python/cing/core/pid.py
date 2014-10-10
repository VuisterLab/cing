#!/usr/bin/env python
#--------------------------------------------------------------------------------------------------------------

import sys
import os

import cing

def makePid( *args ):
    """
    Return Pid object from arguments
    Apply str() on all arguments
    """
    # use str operator on all arguments
    args = map(str, args)
    # could implement some checking here
    # could implement mapping here
    if (len(args) > 0) and (args[0] in Pid.nameMap):
        #args = list(args) # don't know why I have to use the list operator
        args[0] = Pid.nameMap[args[0]]
    #end if
    return Pid( Pid._join(*args) )
#end def
    
    
class Pid( str ):
    """Pid routines, adapted from path idea in: Python Cookbook, A. Martelli and D. Ascher (eds), O'Reilly 2002, pgs 140-142
    Features:
    - newpid = pid1 + id1 
    - slicing to address elements of pid
    - loop over elements of pid
    - Modify an element
    - Copy a pid
    - Incrementation and decrementation
    
    pid = makePid('Residue','mol1','A',507)
    -> Residue:mol1.A.502   (Pid instance)

    pid.type
    -> 'Residue' (str instance)

    pid.id
    -> 'mol1.A.502' (str instance)
    
    pid[0]
    -> Residue (Pid instance)
    
    for id in pid:
        print id
    ->
    'Residue' (str instance)
    'mol1' (str instance)
    'A'  (str instance)
    '502'  (str instance)
    
    pid2 = pid.modify(0, 'Atom') + 'N'
    -> Atom:mol1.A.502.N  (Pid instance)
    
    but also:
    pid3 = pid[0:3] + '100'
    -> Residue:mol1.A.100  (Pid instance)
    
    pid4 = pid.decrement(3,1)
    -> Residue:mol1.A.501  (Pid instance)
    or
    pid4 = pid.increment(3,-1)
    
    pid5 = pid.copy()
    -> Residue:mol1.A.502  (Pid instance)
    
    pid==pid5
    -> True
    
    '502' in pid
    -> True
    """
    
    # name mapping dictionary
    nameMap = dict(
        MO = 'Molecule'
    )

    def __init__(self, string):
        str.__init__(self, string)
        self.version = cing.cingDefinitions.version

    @property
    def type(self):
        parts = self._split()
        if len(parts) > 0:
            return parts[0]
        else:
            return ''
    
    @property
    def id(self):
        parts = self._split()
        if len(parts) > 1:
            return '.'.join(parts[1:])
        else:
            return ''

    def __add__(self, other):
        tmp = self._split() + [other]
        return makePid(*tmp)
    #end def
    
    def __len__(self):
        return len(self._split())
    #end def
    
    def __getslice__( self, start, stop ):
        parts = self._split()[start:stop]
        if len(parts) > 0:
            return makePid(*parts)
        else:
            return Pid('')
    #end def
    
    def __getitem__(self, i):
        return makePid(self._split()[i])
    #end def
    
    def __iter__(self):
        for f in self._split():
            yield f
        #end for
    #end def
    
    def __str__(self):
        return str.__str__(self)
    #end def

    def __repr__(self):
        return 'Pid(%s)' % str.__repr__(self)
    #end def

    def _split(self):
        """
        Return a splitted pid as list or empty list on error
        """
        allParts = []
        
        # Does not work with subsitution of ":" with "." as 'Pid' object does not support item assignment
        parts = self.split(':')
        if len(parts) > 0:
            allParts.append(parts[0])
        if len(parts) > 1:
            for p in parts[1].split('.'):
                allParts.append(p)
        return allParts
    #end def

    @staticmethod
    def _join( *args ):
        """Join args using the rules for constructing a pid
        """
        if len(args) >= 2:
            tmp =':'.join( args[0:2] )
            tmp2 = [tmp] + list(args[2:]) # don't know why args is tuple and thus I have to use
                                          # the list operator to avoid TypeError:
                                          # can only concatenate list (not "tuple") to list?
            return '.'.join(tmp2)
        elif len(args) >= 1:
            return args[0]
        else:
            return ''
    #end def

    def modify(self, index, newId):
        "Return new pid with position index modified by newId"
        parts = self._split()
        parts[index] = newId
        return makePid(*parts)
    #end def

    def increment(self, index, value):
        """Return new pid with position index incremented by value
        Assumes integer valued id at position index
        """
        parts = self._split()
        parts[index] = int(parts[index]) + value
        return makePid(*parts)
    #end def

    def decrement(self, index, value):
        """Return new pid with position index decremented by value
        Assumes integer valued id at position index
        """
        return self.increment(index, value*-1)
    #end def
    
    def copy(self):
        "Return copy of pid"
        # Use makePid to pass it by any 'translater/checking routine'
        parts = self._split()
        return makePid(*parts)
    #end def
#end class
#--------------------------------------------------------------------------------------------------------------

