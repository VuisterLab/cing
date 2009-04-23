from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTsort
from cing.Libs.NTutils import XMLhandler
from cing.core.constants import COLOR_GREEN
from cing.core.constants import COLOR_ORANGE
from cing.core.constants import COLOR_RED

class ROGscore(NTdict):
    """
    Red orange green with comments.
    """
    ROG_COMMENT_NO_COOR = 'No coordinates'
    ROG_COMMENT_POOR_ASSIGNMENT = 'Poor assignment'

    MAX_TO_REPORT_IN_POPUP = 5

    def __init__(self):
        NTdict.__init__(self,
                         __CLASS__  = 'ROGscore',
                         __FORMAT__ = "ROGscore '%(colorLabel)s' %(colorCommentList)s"
                       )
        # Explicitly showing instance attributes here in init.
        self.colorLabel = COLOR_GREEN
        """Elements in this list are tuples of (color, comment).
        """
        self.colorCommentList = NTlist()


    def __str__(self):
        return str(self.colorLabel)

    def reset(self):
        self.colorLabel = COLOR_GREEN
        self.colorCommentList = NTlist()

    def isCritiqued(self):
        if self.colorLabel != COLOR_GREEN:
            return True
        else:
            return False

    def isRed(self):
        return self.colorLabel == COLOR_RED
    def isOrange(self):
        return self.colorLabel == COLOR_ORANGE


    # Thanks to a tip from http://morecavalier.com/index.php?whom=Articles%2FMultiline+TITLES+for+Firefox
    # Can be aligned to left using a better .css.
    def addHTMLkeywords(self, kw):
        pass ##GWV 20 August: problem with this in tables and links
#        if not self.isCritiqued():
#            return
#        if self.colorCommentList:
#            ln = len( self.colorCommentList )
#            subList = self.colorCommentList
#            if ln > self.MAX_TO_REPORT_IN_POPUP:
#                subList = self.colorCommentList[:self.MAX_TO_REPORT_IN_POPUP]
#            kw[ 'cavtitle' ] = '\n'.join( subList )
#            if ln > self.MAX_TO_REPORT_IN_POPUP:
#                kw[ 'cavtitle' ] += '\nand so on for %d comments in total' % ln
#            kw[ 'onmousemove' ] = 'SetCavTimer(event);'
#            kw[ 'onmouseout' ]  = "CancelCavTimer(event);"

    def createHtmlForComments(self, dst):
        if not self.isCritiqued():
            return
        refExists = False
        if refExists:
            for color,comment in self.colorCommentList:
                kw = {'href':''}
                kw['class'] = color
                dst('li' , closeTag=False)
                dst('a' , comment, **kw)
                dst('li' , openTag=False)
    #        dst('ul', openTag=False)
        else:
            for color,comment in self.colorCommentList:
                kw = {'color':color}
                dst('li' , closeTag=False)
                dst('font' , comment, **kw)
                dst('li' , openTag=False)
    #        dst('ul', openTag=False)


    def setMaxColor(self, colorLabel, comment=None):
        """priority: red, orange, green. The so called ROG score.
        The comment is optional and will only be appended when the color lable is
        at least as severe as the current one. The less severe levels of comments
        used to be wiped out but not any more; see issue 153.
        Only ORANGE and RED levels can add comments.
        Parameter comment may also be a list of comments.
        """
    #    if not o.has_key( 'colorLabel' ):# NTlist doesn't have 'has_key'.
    #    if not hasattr(o,'colorLabel'):
    #        o.colorLabel = COLOR_GREEN

        if colorLabel == COLOR_GREEN:
            return

        # certain to stay at or upgrade to given color.
        if colorLabel == COLOR_RED or (colorLabel == COLOR_ORANGE and self.colorLabel != COLOR_RED):
            self.colorLabel = colorLabel

        if not comment:
            return

        if isinstance(comment, list):
            for commentSingle in comment:
               commentTuple = (colorLabel, commentSingle )
               self.colorCommentList.append( commentTuple )# grow list with potentially multiple comments.
        else:
            commentTuple = (colorLabel, comment )
            self.colorCommentList.append(commentTuple)
        self.colorCommentList.removeDuplicates()
        # Keep comments for red and orange together.
        NTsort( self.colorCommentList, 0, inplace=True)
    #end def
#end class

class XMLROGscoreHandler( XMLhandler ):
    """ROCscore XML handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='ROGscore')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs == None: return None
        result = ROGscore()
        result.update(attrs)
        return result
    #end def
#end class
# Initiate an instance
xmlrogscorehandler = XMLROGscoreHandler()