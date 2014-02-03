from collections import OrderedDict
import sys

def formatDictItems(theDict, fmt='{key:20} : {value!s}\n'):
    """Use format on key,value pairs of items of theDict
    """
    return ''.join( [fmt.format(key=k,value=v) for k,v in theDict.items()] )
#end def

class Adict( OrderedDict ):
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

    def getOid(self):
        "Return object id"
        return self.getattrOnly(Adict.OID_STRING)

    def setdefaultKeys(self, fromDict):
        "Set keys of fromDict not present in self to values fromDict"
        for key,value in fromDict.iteritems():
            if key not in self:
                self[key] = value

    def formatItems(self, fmt='{key:20} : {value!s}\n'):
        return formatDictItems(self, fmt)

    def __format__(self, fmt=None):
        if fmt == None or fmt=='':
            return str(self)
        return fmt.format(**self)
    #end def

    def __str__(self):
        clsName = str(self.__class__)[8:-2].split('.')[-1:][0]
        items = self.formatItems('{key}={value!s}, ')[:-2]
        s = '<%s (oid=%d): %s>' % (clsName, self.getOid(), items)
        ls = len(s)
        # restrict the length to MAX_STR_LENGTH
        if ls > Adict.MAX_STR_LENGTH:
            ln = Adict.MAX_STR_LENGTH/2 - 3
            return s[0:ln] + ' .... ' + s[ls-ln:]
        else:
            return s
    #end def

    def toSML(self, stream=sys.stdout):
        if hasattr( self, 'SMLhandler'):
            handler = getattr(self,'SMLhandler')
            handler.toSML(self, stream)
        else:
            nTerror('Adict.toSML: no SMLhandler defined')
        #end if
    #end def

#    def toXML(self, depth=0, stream=sys.stdout, indent='  ', lineEnd='\n'):
#        """
#        Write XML-representation of keys/attributes of self to stream
#        """
#        nTindent(depth, stream, indent)
#        fprintf(stream, "<%s>", self.__class__.__name__)
#        fprintf(stream, lineEnd)
#
#        for a in keys:
#            nTindent(depth+1, stream, indent)
#            fprintf(stream, "<Attr name=%s>", quote(a))
#            fprintf(stream, lineEnd)
#
#            nTtoXML(self[a], depth+2, stream, indent, lineEnd)
#
#            nTindent(depth+1, stream, indent)
#            fprintf(stream, "</Attr>")
#            fprintf(stream, lineEnd)
#        #end for
#        nTindent(depth, stream, indent)
#        fprintf(stream, "</%s>", self.__CLASS__)
#        fprintf(stream, lineEnd)
#    #end def
#end class