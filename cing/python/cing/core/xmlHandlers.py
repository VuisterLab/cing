import cing.core.classes as classes
import cing.Libs.xmlTools as xmlTools
import cing.Libs.io as io
import cing.Libs.NTutils as ntu

class XMLNTplistHandler(xmlTools.XMLhandler):
    """NTplist handler class"""
    def __init__(self):
        xmlTools.XMLhandler.__init__(self, name='plist')
    #end def

    def handle(self, node):
        result = ntu.NTplist()
        for subNode in node.childNodes:
            if (subNode.nodeType == xmlTools.Node.ELEMENT_NODE):
                attrs = xmlTools.nThandle(subNode)
                if attrs == None:
                    return None
                result.update(attrs)
            #end if
        #end for
        return result
    #end def
#end class
#register a handler
ntu.NTplist.XMLhandler = XMLNTplistHandler()


class XMLNTvalueHandler(xmlTools.XMLhandler):
    """NTvalue handler class"""
    def __init__(self):
        xmlTools.XMLhandler.__init__(self, name='NTvalue')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs is None:
            return None
        result = ntu.NTvalue(value = attrs['value'], error = attrs['error'], fmt = attrs['fmt'], fmt2 = attrs['fmt2'])
        result.update(attrs)
        return result
    #end def
#end class
ntu.NTvalue.XMLhandler = XMLNTvalueHandler()


class XMLNTtreeHandler(xmlTools.XMLhandler):
    """NTtree handler class"""
    def __init__(self):
        xmlTools.XMLhandler.__init__(self, name='NTtree')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs is None:
            return None
#       print ">>attrs", attrs
        result = ntu.NTtree(name = attrs['name'])

        # update the attrs values
        result.update(attrs)

        # restore the tree structure
        for child in result._children: # pylint: disable=W0212
#           print '>child>', repr(child)
            result[child.name] = child
            child._parent = result
        return result
    #end def
#end class
ntu.NTtree.XMLhandler = XMLNTtreeHandler()


class XMLNTdictHandler(xmlTools.XMLhandler):
    """NTdict handler class"""
    def __init__(self):
        xmlTools.XMLhandler.__init__(self, name='NTdict')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs is None:
            return None
        result = ntu.NTdict()
        result.update(attrs)
        return result
    #end def
#end class
ntu.NTdict.XMLhandler = XMLNTdictHandler()


#LEGACY
class XMLNTstructHandler(xmlTools.XMLhandler):
    """NTstruct handler class"""
    def __init__(self):
        xmlTools.XMLhandler.__init__(self, name='NTstruct')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs is None:
            return None
        result = ntu.NTdict()
        result.update(attrs)
        return result
    #end def
#end class
ntstructhandler = XMLNTstructHandler()


class XMLNTlistHandler(xmlTools.XMLhandler):
    """NTlist handler class"""
    def __init__(self):
        xmlTools.XMLhandler.__init__(self, name='NTlist')
    #end def

    def handle(self, node):
        items = self.handleMultipleElements(node)
        if items is None:
            return None
        result = ntu.NTlist()
        for item in items:
            result.append(item)
        return result
    #end def
#end class
ntu.NTlist.XMLhandler = XMLNTlistHandler()


#LEGACY:
class XMLHistoryHandler(xmlTools.XMLhandler):
    """History handler class"""
    def __init__(self):
        xmlTools.XMLhandler.__init__(self, name = 'History')
    #end def

    def handle(self, node):
        items = self.handleMultipleElements(node)
        if items is None:
            return None
        result = classes.History()
        for item in items:
            result.append(item)
        return result
    #end def
#end class
#register this handler
historyhandler = XMLHistoryHandler()


# #LEGACY:
class XMLProjectHandler(xmlTools.XMLhandler):
    """Project handler class"""
    def __init__(self):
        xmlTools.XMLhandler.__init__(self, name = 'Project')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs is None:
            return None
        result = classes.Project(name = attrs['name'])

        # update the attrs values
        result.update(attrs)

        return result
    #end def
#end class
#register this handler
projecthandler = XMLProjectHandler()


#class XMLMoleculeHandler( XMLhandler ):
#    """Molecule handler class"""
#    def __init__( self ):
#        XMLhandler.__init__( self, name='Molecule')
#    #end def
#
#    def handle( self, node ):
#        attrs = self.handleDictElements( node )
#        if attrs == None: return None
#        result = Molecule( name = attrs['name'] )
#
#        # update the attrs values
#        result.update( attrs )
#
#        # restore the tree structure
#        for child in result._children:
##           print '>child>', repr(child)
#            result[child.name] = child
#            child._parent = result
#        return result
#    #end def
##end class
#
##register this handler
#Molecule.XMLhandler = XMLMoleculeHandler()

#class XMLChainHandler( XMLhandler ):
#    """Chain handler class"""
#    def __init__( self ):
#        XMLhandler.__init__( self, name='Chain')
#    #end def
#
#    def handle( self, node ):
#        attrs = self.handleDictElements( node )
#        if attrs == None: return None
#        result = Molecule( name = attrs['name'] )
#
#        # update the attrs values
#        result.update( attrs )
#
#        # restore the tree structure and references
#        for res in result._children:
##           print '>child>', repr(child)
#            result[res.name] = res
#            result[res.shortName] = res
#            result[res.resNum] = res
#            res._parent = result
#        return result
#    #end def
##end class
#
##register this handler
#Chain.XMLhandler = XMLChainHandler()

#class XMLAtomHandler( XMLhandler ):
#    """Atom handler class"""
#    def __init__( self ):
#        XMLhandler.__init__( self, name='Atom')
#    #end def
#
#    def handle( self, node ):
#        attrs = self.handleDictElements( node )
#        if attrs == None: return None
#        result = Atom( resName = attrs['resName'], atomName = attrs['name'] )
#
#        # update the attrs values
#        result.update( attrs )
#
#        # restore the resonance references
#        for r in result.resonances:
#            r.atom = result
#
#        return result
#    #end def
##end class
##register this handler
#Atom.XMLhandler = XMLAtomHandler()



