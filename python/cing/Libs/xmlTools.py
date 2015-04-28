"""
LEGACY XML code

"""
import sys

#from xml.dom import minidom, Node
import xml.dom.minidom as minidom
from xml.dom import Node
from xml.sax import saxutils
from string  import find

import cing.Libs.io as io
from cing.Libs.io import fprintf

XMLhandlers             = {}


def nTindent(depth, stream, indent):
    """
    Indent stream to depth; to pretty format XML
    """
    for dummy in range(depth):
        fprintf(stream, indent)
    #end for
#end def


def quote(inputString):
    "return a single or double quoted string"
    single = (find(inputString, "'") >= 0)
    double = (find(inputString, '"') >= 0)
    if single and double:
        io.error("in quote: both single and double quotes in [{0}]\n", inputString)
        return None
    if double:
        return "'" + inputString + "'"
    return '"' + inputString + '"'
#end def


class XMLhandler:
    """Generic handler class

       methods:
       __init__                 : will register the handler in XMLhandlers
       handle                   : to be implemented in specific handler
       handleSingleElement      : for float,int,string etc)
       handleMultipleElements   : for list, tuple
       handleDictElements       : for dict, NTdict and the like

    """
    def __init__(self, name):
        global XMLhandlers # pylint: disable=W0602
        self.name = name
        XMLhandlers[name] = self
    #end def

    def handle(self, node):
        'A do nothing method.'
        pass
    #end def

    def handleSingleElement(self, node):
        """Returns single element below node from DOM tree"""
        self.printDebugNode(node)
        if node.nodeName != self.name:
            io.error('XML%sHandler: invalid XML handler for node <{0}>\n', node.nodeName)
            return None
        #end if
        if len(node.childNodes) != 1:
            io.error("XML%sHandler: malformed DOM tree ({0})\n", self.name)
            return None
        #end if
        if node.childNodes[0].nodeType != Node.TEXT_NODE:
            io.error("XML%sHandler: malformed DOM tree ({0}), expected TEXT_NODE containing value\n", self.name)
            return None
        #end if
        result = node.childNodes[0].nodeValue
#        nTdebug("==>%s %s",repr(node), result)
        return result
    #end def

    def handleMultipleElements(self, node):
        'For each child handle XML'
        self.printDebugNode(node)
        if node.nodeName != self.name:
            io.error('XML%Handler: invalid XML handler for node <{0}>\n', node.nodeName)
            return None
        #end if
        result = []
        for subNode in node.childNodes:
            if subNode.nodeType == Node.ELEMENT_NODE:
                result.append(nThandle(subNode))
            #end if
        #end for
#        nTdebug("==>%s %s",repr(node), result)
        return  result
    #end def

    def handleDictElements(self, node):
        'For dictionary elements return another dictionary.'
        self.printDebugNode(node)
        if node.nodeName != self.name:
            io.error('XML%sHandler: invalid XML handler for node <{0}>\n', node.nodeName)
            return None
        #end if

        result = {}

# We have two dict formats
# original 'NT' format:
##
##<dict>
##    <key name="noot">
##        <int>2</int>
##    </key>
##    <key name="mies">
##        <int>3</int>
##    </key>
##    <key name="aap">
##        <int>1</int>
##    </key>
##</dict>
##
# Or Apple plist dict's
##<dict>
##      <key>Key</key>
##      <string>3F344E56-C8C2-4A1C-B6C7-CD84EAA1E70A</string>
##      <key>Title</key>
##      <string>New on palm</string>
##      <key>Type</key>
##      <string>com.apple.ical.sources.naivereadwrite</string>
##</dict>

        # first collect all element nodes, skipping the 'empty' text nodes
        subNodes = []
        for n in node.childNodes:
#            print '>>',n
            if n.nodeType == Node.ELEMENT_NODE:
                subNodes.append(n)
        #end for
        if len(subNodes) == 0:
            return result

        #append all keys, checking for 'format' as outlined above
        i = 0
        while (i < len(subNodes)):
            #print '>>', len(subNodes), i, str(subNodes[i]), 'childnodes:', len(subNodes[i].childNodes), str(subNodes[i].childNodes[0])
            self.printDebugNode(subNodes[i])

            try:
                keyName = subNodes[i].attributes.get('name').nodeValue
                #test for valid childNodes; have seen cases they don't exits (!?)
                if len(subNodes[i].childNodes) > 1:
                    value = nThandle(subNodes[i].childNodes[1])
                else:
                    #nTdebug('XMLhandler.handleDictElements: empty key "%s", value set to None', keyName)
                    value = None
                i += 1
            except AttributeError:
                keyName = subNodes[i].childNodes[0].nodeValue
                value = nThandle(subNodes[i+1])
                i += 2

#            print ">>", keyName, value
            result[keyName] = value
        #end while
#        nTdebug("==>%s %s",repr(node), result)
        return result
    #end def

    def printDebugNode(self, node):
        'Flip this method on when needing output for debugging.'
        pass
#        nTdebug("   %s, type %s, subnodes %d", str(node), node.nodeType, len(node.childNodes) )
    #end def
#end class


class XMLNoneHandler(XMLhandler):
    """None handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='None')
    #end def

    def handle(self, node):
        return None
    #end def
#end class

class XMLintHandler(XMLhandler):
    """int handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='int')
    #end def

    def handle(self, node):
        result = self.handleSingleElement(node)
        if result == None:
            return None
        return int(result)
    #end def
#end class


class XMLboolHandler(XMLhandler):
    """bool handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='bool')
    #end def

    def handle(self, node):
        result = self.handleSingleElement(node)
        if result == None:
            return None
        # NB: bool('False') returns True!
        return bool(result=='True')
    #end def
#end class


class XMLfloatHandler(XMLhandler):
    """float handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='float')
    #end def

    def handle(self, node):
        result = self.handleSingleElement(node)
        if result == None:
            return None
        return float(result)
    #end def
#end class


class XMLstringHandler(XMLhandler):
    """string handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='string')
    #end def

    def handle(self, node):
        # strings can be empty
        if len(node.childNodes) == 0:
            return ''

        result = self.handleSingleElement(node)
        if result == None:
            return None
        return str(saxutils.unescape(result))
    #end def
#end class


class XMLunicodeHandler(XMLhandler):
    """unicode handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='unicode')
    #end def

    def handle(self, node):
        # strings can be empty
        if len(node.childNodes) == 0:
            return unicode('')

        result = self.handleSingleElement(node)
        if result == None:
            return None
        return unicode(saxutils.unescape(result))
    #end def
#end class


class XMLlistHandler(XMLhandler):
    """list handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='list')
    #end def

    def handle(self, node):
        result = self.handleMultipleElements(node)
        if result == None:
            return None
        return result
    #end def
#end class


class XMLtupleHandler(XMLhandler):
    """tuple handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='tuple')
    #end def

    def handle(self, node):
        result = self.handleMultipleElements(node)
        if result == None:
            return None
        return tuple(result)
    #end def
#end class


class XMLdictHandler(XMLhandler):
    """dict handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='dict')
    #end def

    def handle(self, node):
        result = self.handleDictElements(node)
        if result == None:
            return None
        return result
    #end def
#end class

#define one instance of the handlers
nonehandler     = XMLNoneHandler()
inthandler      = XMLintHandler()
boolhandler     = XMLboolHandler()
floathandler    = XMLfloatHandler()
stringhandler   = XMLstringHandler()
unicodehandler  = XMLunicodeHandler()
listhandler     = XMLlistHandler()
tuplehandler    = XMLtupleHandler()
dicthandler     = XMLdictHandler()


def nThandle(node):
    """Handle a given node, return object of None in case of Error
    """
    if node is None:
        io.error("nThandle: None node\n")
        return None
    #end if
    if node.nodeName not in XMLhandlers:
        io.error('nThandle: no handler for XML <{0}>\n', node.nodeName)
        return None
    #end if
    return XMLhandlers[node.nodeName].handle(node)
#end def


def nTtoXML(obj, depth=0, stream=sys.stdout, indent='\t', lineEnd='\n'):
    """Generate XML:
       check for method toXML
       or
       standard types int, float, tuple, list, dict
    """
    if (obj == None):
        nTindent(depth, stream, indent)
        fprintf(stream, "<None/>")
        fprintf(stream, lineEnd)
    elif hasattr(obj, 'toXML'):
        obj.toXML(depth, stream, indent, lineEnd)
    elif (type(obj) == int):
        nTindent(depth, stream, indent)
        fprintf(stream, "<int>%s</int>", repr(obj))
        fprintf(stream, lineEnd)
    elif (type(obj) == bool):
        nTindent(depth, stream, indent)
        fprintf(stream, "<bool>%s</bool>", repr(obj))
        fprintf(stream, lineEnd)
    elif (type(obj) == float):
        nTindent(depth, stream, indent)
        fprintf(stream, "<float>%s</float>", repr(obj))
        fprintf(stream, lineEnd)
    elif (type(obj) == str):
        nTindent(depth, stream, indent)
#        fprintf( stream, "<string>%s</string>",  saxutils.escape( obj )  )
        fprintf(stream, "<string>%s</string>", unicode(saxutils.escape(obj)))
        fprintf(stream, lineEnd)
    elif (type(obj) == unicode):
        nTindent(depth, stream, indent)
        fprintf(stream, "<unicode>%s</unicode>", unicode(saxutils.escape(obj)))
        fprintf(stream, lineEnd)
    elif (type(obj) == list):
        nTindent(depth, stream, indent)
        fprintf(stream, "<list>")
        fprintf(stream, lineEnd)
        for a in obj:
            nTtoXML(a, depth+1, stream, indent, lineEnd)
        #end for
        nTindent(depth, stream, indent)
        fprintf(stream, "</list>")
        fprintf(stream, lineEnd)
    elif (type(obj) == tuple):
        nTindent(depth, stream, indent)
        fprintf(stream, "<tuple>")
        fprintf(stream, lineEnd)
        for a in list(obj):
            nTtoXML(a, depth+1, stream, indent, lineEnd)
        #end for
        nTindent(depth, stream, indent)
        fprintf(stream, "</tuple>")
        fprintf(stream, lineEnd)
    elif (type(obj) == dict):
        nTindent(depth, stream, indent)
        fprintf(stream, "<dict>")
        fprintf(stream, lineEnd)
        for key, value in obj.iteritems():
            nTindent(depth+1, stream, indent)
            fprintf(stream, "<key name=%s>", quote(key))
            fprintf(stream, lineEnd)
            nTtoXML(value, depth+2, stream, indent, lineEnd)
            nTindent(depth+1, stream, indent)
            fprintf(stream, "</key>")
            fprintf(stream, lineEnd)
        #end for
        nTindent(depth, stream, indent)
        fprintf(stream, "</dict>")
        fprintf(stream, lineEnd)
    else:
        pass
        io.error('nTtoXML: undefined object "{0}": cannot generate XML\n', obj) # reenable when done testing.
    #end if
#end def


def obj2XML(obj, stream=None, path=None):
    """Convert an object to XML
       output to stream or path
       gwv 13 Jun08: return object or None on error
    """
    if obj is None:
        io.error("obj2XML: no object\n")
        return None
    if stream is None and path is None:
        io.error("obj2XML: no output defined\n")
        return None

    closeFile = 0
    if not stream:
        stream = open(path, 'w')
        closeFile = 1

    fprintf(stream, '<?xml version="1.0" encoding="ISO-8859-1"?>\n')
    nTtoXML(obj, depth=0, stream=stream, indent='    ')

    if closeFile:
        stream.close()

    return obj
#end def

def xML2obj(path=None, string=None):
    """Convert XML file to object
       returns object or None on error
    """
    if path == None and string==None:
        io.error("xML2obj: no input defined\n")
        return None

#    nTdebug("Starting to read XML from path: " + repr(path)+ " or string: " + repr(string))
    if path:
        doc = minidom.parse(path)
    else:
        doc = minidom.parseString(string)
#    nTdebug("Done reading XML")
    root = doc.documentElement

    result = nThandle(root)
    doc.unlink()
    return result
#end def
