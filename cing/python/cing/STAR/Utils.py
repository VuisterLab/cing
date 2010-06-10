"""
Just a few utilities that can be of more general use.
"""
from cing.Libs.NTutils import * #@UnusedWildImport

__author__    = "$Author$"
___revision__ = "$Revision$"
___date__     = "$Date$"


"""
A fast transposing algorithm from the python mailing list
Used in TagTable.
"""
def transpose ( matrix ):
    if len( matrix ) < 1:
        NTerror(' trying to transpose an empty matrix')
        return 1
    elif len( matrix ) == 1:
        if len(matrix[0]) == 0:
            NTerror(' trying to transpose an empty matrix, shape would be lost')
            NTerror(' [[]] would become []')
            return 1
        else:
            return map( lambda y : (y)   , matrix[0] )
    else:
        return apply( map, [None,] + list(matrix) )


"""
Collapses all whitespace to a single regular space
before comparing. Doesn't remove final eol space.
"""
def equalIgnoringWhiteSpace( a, b):
    pattern   = re.compile("\s+" )
    a = re.sub(pattern, ' ',a)
    b = re.sub(pattern, ' ',b)
#    print "a["+a+"]"
#    print "b["+b+"]"
    return a == b

def dos2unix(text):
    return re.sub('\r\n', '\n',text)
def unix2dos(text):
    return re.sub('([^\r])(\n)', '\1\r\n',text)
def mac2unix(text):
    return re.sub('\r', '\n',text)
