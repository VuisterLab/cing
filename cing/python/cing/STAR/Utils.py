"""
Just a few utilities that can be of more general use.
"""
from cing.Libs.NTutils import * #@UnusedWildImport

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

def getHumanTagName(tagName):
    "Replace _ by a space"
    return tagName.replace('_', ' ')