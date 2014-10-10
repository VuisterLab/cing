from collections import OrderedDict
#import sys

from cing.Libs import io


class Adict(OrderedDict):
    """A dict that maps keys onto attributes; as NTdict, but cleaner (?) and less overhead?
    methods setattrOnly, getattrOnly and delattrOnly allow for 'oldstyle' non-key-mapped attributes
    """
    MAX_STR_LENGTH = 120
    # Object id
    nextOid = 0
    OID_STRING = '_oid'

    def __init__(self, *args, **kwds):
        """
    Initialize an ordered dictionary with mapped keys.  The signature is the same as
    regular dictionaries, but keyword arguments are not recommended because
    their insertion order is arbitrary.
        """
        OrderedDict.__init__(self, *args, **kwds)
        self.setattrOnly(Adict.OID_STRING, Adict.nextOid)
        Adict.nextOid += 1
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
            raise AttributeError('Attribute (keyed) "%s" not found.' % attr)
        return self[attr]
    #end def

    def __setattr__(self, attr, value):
        """Implement basic functionality:
           Keys can be referenced as in dictionary methods, or as an attribute.
        """
        #print '>> in __setattr__', attr, value
        # preserve OrderedDict implementation attributes
        if attr.startswith('_Ordered'):
            OrderedDict.__setattr__(self, attr, value)
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
            OrderedDict.__delattr__(self, attr)
        else:
            del(self[attr])
    #end def

    def getattrOnly(self, attr):
        """Get 'Old-style' attribute, not mapped to key
        """
        # OrderedDict does not have a __getattr__ method
        #print ">>", self.__dict__.keys()
        if not attr in self.__dict__.keys():
            raise AttributeError('Attribute (only): "%s" not found.' % attr)
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
        del(self.__dict__[attr])
    #end def

    def getOid(self):
        "Return object id"
        return self.getattrOnly(Adict.OID_STRING)

    def setdefaultKeys(self, fromDict):
        """Set keys of fromDict not present in self to values fromDict"""
        for key, value in fromDict.iteritems():
            if key not in self:
                self[key] = value

    def formatItems(self, fmt='{key:20} : {value!s}\n'):
        return io.formatDictItems(self, fmt)

    def __format__(self, fmt=None):
        if fmt is None or fmt == '':
            return str(self)
        return fmt.format(**self)
    #end def

    def __str__(self):
#        clsName = str(self.__class__)[8:-2].split('.')[-1:][0]
        clsname = self.__class__.__name__
        items = self.formatItems('{key}={value!s}, ')[:-2]
        s = '<%s (oid=%d): %s>' % (clsname, self.getOid(), items)
        ls = len(s)
        # restrict the length to MAX_STR_LENGTH
        if ls > Adict.MAX_STR_LENGTH:
            ln = Adict.MAX_STR_LENGTH/2 - 3
            return s[0:ln] + ' .... ' + s[ls-ln:]
        else:
            return s
    #end def
#end class
