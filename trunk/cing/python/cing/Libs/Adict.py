from collections import OrderedDict

def formatItems(theDict, fmt='{key:10} : {value}\n'):
    """Use format on key,value pairs of items of theDict
    """
    return ''.join( [fmt.format(key=k,value=v) for k,v in theDict.items()] )
#end def

class Adict( OrderedDict ):
    """A dict that maps keys onto attributes; as NTdict, but cleaner (?) and less overhead?
    methods setattrOnly, getattrOnly and delattrOnly allow for 'oldstyle' non-key-mapped attributes
    """
    nextId = 0

    def __init__(self, *args, **kwds):
        """
    Initialize an ordered dictionary with mapped keys.  The signature is the same as
    regular dictionaries, but keyword arguments are not recommended because
    their insertion order is arbitrary.
        """
        OrderedDict.__init__(self, *args, **kwds)
        self.setattrOnly('_id', Adict.nextId)
        Adict.nextId += 1
    #end def
    #------------------------------------------------------------------
    # Basic functionality
    #------------------------------------------------------------------
    def __getattr__(self, attr):
        """Implement basic functionality:
           Keys can be referenced as in dictionary methods, or as an attribute.
        """
        #print '>> in __getattr__', attr
        # preserve OrderedDict implementation attributes
        if attr.startswith('_Ordered'):
            # OrderedDict does not have a __getattr__ method
            return self.getattrOnly(attr)

        if not attr in self:
            raise AttributeError( 'Attribute (keyed) "%s" not found.' % attr )
        return self[attr]
    #end def

    def __setattr__(self, attr, value):
        """Implement basic functionality:
           Keys can be referenced as in dictionary methods, or as an attribute.
        """
        #print '>> in __setattr__', attr, value
        # preserve OrderedDict implementation attributes
        if attr.startswith('_Ordered'):
            OrderedDict.__setattr__( self, attr, value )
        else:
            self[attr] = value
    #end def

    def __delattr__(self, attr):
        """Implement basic functionality:
           Keys can be referenced as in dictionary methods, or as an attribute.
        """
        #print '>> in __delattr__', attr
        # preserve OrderedDict implementation attributes
        if attr in self.__dict__.keys():
            OrderedDict.__delattr__( self, attr )
        else:
            del(self[attr])
    #end def

    def getattrOnly(self, attr):
        """Get 'Old-style' attribute, not mapped to key
        """
        # OrderedDict does not have a __getattr__ method
        if not attr in self.__dict__:
            raise AttributeError( 'Attribute (only): "%s" not found.' % attr )
        return self.__dict__[attr]
    #end def

    def setattrOnly(self, attr, value):
        """'Set 'Old-style' attribute, not mapped to key
        """
        self.__dict__[attr] = value
    #end def

    def delattrOnly(self, attr):
        """'delete 'Old-style' attribute, not mapped to key
        """
        del( self.__dict__[attr] )
    #end def

    def formatItems(self, fmt='{key:10} : {value}\n'):
        return formatItems(self, fmt)

    def __format__(self, fmt=None):
        if fmt == None:
            return str(self)
        return fmt.format(**self)
    #end def
#end class