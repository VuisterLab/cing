"""
Version 2/3 Pid routines
"""
import cing
import cing.Libs.io as io


def decodePid(sourceObject, thePid):
    """
    try to decode thePid relative to sourceObject
    return decoded pid object or None on not found or Error
    """
    if thePid is None:
        return None

    # assure a Pid object
    if not isinstance(thePid, Pid):
        if hasattr(thePid, 'asPid'):
            thePid = thePid.asPid()
        else:
            # just try
            thePid = Pid(str(thePid))
        #end if
    #end if

    if not thePid.isValid:
        io.error('decodePid: pid "{0}" is invalid', thePid)
        return None
    #end if

    # check if thePid describes the source object
    if hasattr(sourceObject,'asPid'):
        sourcePid = sourceObject.asPid()
        if sourcePid == thePid:
            return sourceObject
    #end if
    # apparently not, let try to traverse down to find the elements of thePid
    obj = sourceObject
    for p in thePid:
        #print( 'decodePid>>', p, object)
        if p not in obj:
            return None
        obj = obj[p]
    #end for
    # found an object, check if it is the right kind
    if thePid.type != obj.__class__.__name__:
        io.error('decodePid: type "{0}" does not match object type "{1}"',
                 thePid.type, obj.__class__.__name__)
        return None
    return obj
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
    
    pid = Pid('Residue','mol1','A',502)
    -> Residue:mol1.A.502   (Pid instance)

    pid.type
    -> 'Residue' (str instance)

    pid.id
    -> 'mol1.A.502' (str instance)
    
    pid[0]
    -> 'mol1' (str instance)

    pid[0:3]
    -> 'mol1.A.502' (str instance)
    
    for id in pid:
        print id
    ->
    'mol1' (str instance)
    'A'  (str instance)
    '502'  (str instance)
    
    pid2 = pid.modify(1, 'B', type='Atom') + 'N'
    -> Atom:mol1.B.502.N  (Pid instance)
    
    but also:
    pid3 = Pid('Residue') + 'mol2'
    -> Residue:mol2  (Pid instance)
    
    pid4 = pid.decrement(2,1)
    -> Residue:mol1.A.501  (Pid instance)
    or
    pid4 = pid.increment(2,-1)
    
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
        str.__init__(string)

        self._version = 'cing:%s' % cing.cingDefinitions.version

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
    #end def

    @property
    def isValid(self):
        # tests here
        if self.find(':') < 0:
            return False
        parts = self._split()
        if len(parts) < 2:
            return False
        # passed all test; return True
        return True

    @property
    def str(self):
        return str(self)

    def __add__(self, other):
        tmp = self._split() + [other]
        #print 'Pid.__add__', tmp
        return Pid.new(*tmp)
    #end def
    
    def __len__(self):
        return len(self._split())
    #end def
    
    def __getslice__(self, start, stop):
        parts = self._split()[start+1:stop+1]
        if len(parts) > 0:
            return '.'.join(*parts)
        else:
            return ''
    #end def
    
    def __getitem__(self, i):
        return self._split()[i+1]
    #end def
    
    def __iter__(self):
        for f in self._split()[1:]:
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
        
        # Does not work with subsitution of ":" with "." as 'Pid' object does not support
        # item assignment
        parts = self.split(':')
        if len(parts) > 0:
            allParts.append(parts[0])
        if len(parts) > 1:
            for p in parts[1].split('.'):
                allParts.append(p)
        return allParts
    #end def

    @staticmethod
    def new( *args ):
        """
        Return Pid object from arguments
        Apply str() on all arguments
        Have to use this as intermediate as str baseclass of Pid only accepts one argument
        """
        # use str operator on all arguments
        args = map(str, args)
        # could implement could implement mapping here
        if (len(args) > 0) and (args[0] in Pid.nameMap):
            #args = list(args) # don't know why I have to use the list operator
            args[0] = Pid.nameMap[args[0]]
        #end if
        return Pid( Pid._join(*args) )
    #end def

    @staticmethod
    def _join(*args):
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

    def modify(self, index, newId, type=None):
        "Return new pid with position index modified by newId"
        parts = self._split()
        if index+1 >= len(parts):
            io.error('Pid.modify: invalid index ({0})\n', index+1)
        parts[index+1] = newId
        if type is not None:
            parts[0] = type
        return Pid.new(*parts)
    #end def

    def increment(self, index, value):
        """Return new pid with position index incremented by value
        Assumes integer valued id at position index
        """
        parts = self._split()
        parts[index+1] = int(parts[index+1]) + value
        return Pid.new(*parts)
    #end def

    def decrement(self, index, value):
        """Return new pid with position index decremented by value
        Assumes integer valued id at position index
        """
        return self.increment(index, value*-1)
    #end def
    
    def copy(self):
        "Return copy of pid"
        # Use Pid.new to pass it by any 'translater/checking routine'
        parts = self._split()
        return Pid.new(*parts)
    #end def
#end class
#--------------------------------------------------------------------------------------------------------------

