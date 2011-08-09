"""
Classes for dealing with STAR syntax
"""
from cing.Libs.NTutils import * #@UnusedWildImport
class SaveFrame (Lister):
    """
    Saveframe class
    """
    def __init__( self,
                  title     = 'general_sf_title',
                  tagtables = None,
                  text      = '',
                  verbosity = 2,
                  comment = ''):
        Lister.__init__(self)
        self.title      = title

        # Modified tagtables initialization so list references
        # are not carried through (Wim 14/07/2002)
        self.tagtables = tagtables

        if self.tagtables == None:
            self.tagtables  = []

        self.text       = text
        self.verbosity  = verbosity
        self.comment = comment          # Comment attribute added to node (Wim 2003/08/05)

    def star_text (self,
                   flavor = 'NMR-STAR'
                   ):
        "Returns the STAR text representation"
        str = "\n"
        str = str + 'save_%s\n' % self.title

        for tagtable in self.tagtables:
            str = str + tagtable.star_text( flavor=flavor )

        str = str + '\nsave_\n'
        return str

    def check_integrity( self,  recursive = 1  ):
        "Simple checks on integrity"
        if recursive:
            for tagtable in self.tagtables:
                if tagtable.check_integrity():
                    print "ERROR: integrity check failed for tagtable"
                    return 1
        if self.verbosity >= 9:
            print 'Checked integrity of SaveFrame(%2s tagtables, recurs.=%s)  : OK [%s]' % (
                len(self.tagtables), recursive, self.title )

    def getSaveFrameCategory(self)   :
        """
        Or print Warning and return None
        """
        possibleTagNamesSFCategory = [ '_Saveframe_category',  # 2.1
                                       '.Sf_category' ]        # 3
        if not self.tagtables:
            nTwarning('no tagtable found in Saveframe')
            return None

        tT = self.tagtables[0] # assumed 0
        if not tT.tagvalues[0]: # assumed 0
            nTwarning('empty tagtable found in Saveframe')
            return None
        found = 0
        for possi in possibleTagNamesSFCategory:
            if tT.tagnames[0].endswith(possi):
                found = 1
        if not found:
            nTwarning("first tag doesn't look like a Sf_category; taking value anyway")

        return tT.tagvalues[0][0]

