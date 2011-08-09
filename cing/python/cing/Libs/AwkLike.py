from cing.Libs.NTutils import * #@UnusedWildImport

class AwkLike:
    """
    Awk-like functionality

    defines:
        NR
        NF
        FILENAME
        dollar[0 , ... , NF]

        use as:

     for line in AwkLike('myfile'):
         if line.NF > 1:
             print line.dollar[0], line.dollar[1]

        JFD adds: iterations routine
        fails on parsing entry 1o9l whatif's pdbout.txt when called in a naive way.
        If the number of fields is less than required it runs out of recursion depth.
        Workaround, don't filter here but outside the loop.
    """

    def __init__(self, filename=None, minLength = -1, commentString = None, minNF = -1,
                 skipHeaderLines = 0, separator = None ):
        if filename:
            self.FILENAME = filename
            if not os.path.exists(filename):
                nTerror("Failed to find: [%s]" % filename)
            else:
                self.f = open(filename,'r')
        else:
            self.f = sys.stdin
            self.FILENAME = 'stdin'

        self.minLength = minLength
        self.commentString = commentString
        self.minNF = minNF
        self.skipHeaderLines = skipHeaderLines

        self.NR = 0
        self.NF = 0
        self.dollar = []
        self.separator = separator


    def __iter__( self ):
        return self

    def next( self ):
        """iterations routine
        JFD fails on parsing entry 1o9l whatif's pdbout.txt when called in a naive way.
        If the number of fields is less than required it runs out of recursion depth.
        Workaround, don't filter here but outside the loop.
        """
        if not self.f:
            raise StopIteration

        self.line = self.f.readline()
        self.dollar = [self.line[:-1]] # -1 for excluding line terminator.
#        print 'line:        [' + repr(self.line)  + ']'
        if len(self.line):
            self.NR += 1
            for f in self.line.split(self.separator):
                # Skip everything after the comment?
                if self.commentString and f.startswith(self.commentString):
#                    nTdebug("Skipping fields after comment on line: [%s]" % self.line)
#                    nTdebug("   parsed so far: %s" % repr(self.dollar) )
                    break
#                nTdebug("Appending to parsed: [%s]" % f)
                self.dollar.append( f )
            self.NF = len(self.dollar)-1
            if self.minLength >= 0:
                if len(self.dollar[0]) < self.minLength:
#                    nTdebug("Skipping line with less than required number of characters: [%s]" % self.line)
                    return self.next()
            if self.minNF > 0:
                if self.NF < self.minNF:
#                    nTdebug("Skipping line with less than required number of fields: [%s]" % self.line)
                    return self.next()
            if self.commentString:
                if self.isComment( self.commentString ):
#                    nTdebug("Skipping comment line: [%]" % self.line)
                    return self.next()
            if self.skipHeaderLines >= self.NR:
#                nTdebug('skipping header line [%d] which is less than or equal to [%s]' % (
#                    self.NR, self.skipHeaderLines))
                return self.next()
            return self
        self.close()
        raise StopIteration
    #end def


    def close( self ):
        """internal routine"""
        if not self.f:
            nTerror("Can't close the file because it was not present.")
            return
        self.f.close()
        self.f = None

    def float( self, field ):
        """Return field converted to float """
        try:
            return float( self.dollar[ field ] )
        except ValueError:
            nTerror('AwkLike: expected float for "%s" (file: %s, line %d: "%s")',
                    self.dollar[field],
                    self.FILENAME,
                    self.NR,
                    self.dollar[0]
                    )
        except IndexError:
            nTerror('AwkLike: invalid field number "%d" (file: %s, line %d: "%s")',
                    field,
                    self.FILENAME,
                    self.NR,
                    self.dollar[0]
                    )
    def int( self, field ):
        """Return field converted to int """
        try:
            return int( self.dollar[ field ] )
        except ValueError:
            nTerror('AwkLike: expected integer for "%s" (file: %s, line %d: "%s")',
                    self.dollar[field],
                    self.FILENAME,
                    self.NR,
                    self.dollar[0]
                    )
        except IndexError:
            nTerror('AwkLike: invalid field number "%d" (file: %s, line %d: "%s")',
                    field,
                    self.FILENAME,
                    self.NR,
                    self.dollar[0]
                    )

    def printit( self ):
        nTmessage( '==>%s NR=%d NF=%d' % (self.FILENAME, self.NR, self.NF))
        i=0
        for field in self.dollar:
            nTmessage( '%3d >%s<' % (i, field) )
            i += 1
        return 0

    def isComment( self, commentString = '#'):
        """check for commentString on start of line
           return None or 1
        """
        if self.dollar[0].strip().startswith( commentString ):
            return 1
        return None

    def isEmpty( self ):
        return self.NF == 0
#
#==============================================================================
#
class AwkLikeS:
    """
        Awk-like functionality on string

        defines:
            NR
            NF
            FILENAME = 'string'
            dollar[0 ... NF]

        use as:

        for line in AwkLikeS('myString'):
            if line.NF > 1:
                print line.dollar[0], line.dollar[1]
    """

    def __init__(self, str, minLength = -1, commentString = None, minNF = -1):

        if (not str) or (len(str)<=0):
            self.lines = None
            return None

        self.lines = str.splitlines()
        self.MAX_NR = len( self.lines)

        self.minLength = minLength
        self.commentString = commentString
        self.minNF = minNF

        self.NR = 0
        self.NF = 0
        self.dollar = []
        self.FILENAME = 'string'

    def __iter__( self ):
        return self

    def next( self ):
        """iterations routine"""
        if (not self.lines) or (self.NR >= self.MAX_NR):
            raise StopIteration
#            return None

        else:
            self.line = self.lines[self.NR]

            self.dollar = [self.line]
            for f in self.line.split():
                self.dollar.append( f )
            #end for
            self.NF = len(self.dollar)-1
            self.NR += 1

            # check if we need to skip this line
            if (self.minLength >= 0 and len(self.dollar[0]) < self.minLength):
                return self.next()
            #end if
            if (self.minNF > 0 and self.NF < self.minNF):
                return self.next()
            #end if
            if (self.commentString != None and self.isComment( self.commentString )):
                return self.next()
            #end if

            return self
        #end if
    #end def

    def float( self, field ):
        """Return field converted to float """
        try:
            return float( self.dollar[ field ] )
        except ValueError:
            nTerror('AwkLike: expected float for "%s" (file: %s, line %d: "%s")',
                    self.dollar[field],
                    self.FILENAME,
                    self.NR,
                    self.dollar[0]
                    )
        except IndexError:
            nTerror('AwkLike: invalid field number "%d" (file: %s, line %d: "%s")',
                    field,
                    self.FILENAME,
                    self.NR,
                    self.dollar[0]
                    )
        #end try
        return None

    def int( self, field ):
        """Return field converted to int """
        try:
            return int( self.dollar[ field ] )
        except ValueError:
            nTerror('AwkLike: expected integer for "%s" (file: %s, line %d: "%s")',
                    self.dollar[field],
                    self.FILENAME,
                    self.NR,
                    self.dollar[0]
                    )
        except IndexError:
            nTerror('AwkLike: invalid field number "%d" (file: %s, line %d: "%s")',
                    field,
                    self.FILENAME,
                    self.NR,
                    self.dollar[0]
                    )
        #end try
        return None

    def printit( self ):
        print '%s ==> NR=%d NF=%d' % (self.FILENAME, self.NR, self.NF)
        i=0
        for field in self.dollar:
            print '%3d >%s<' % (i, field)
            i += 1
        return 0

    def isComment( self, commentString = '#'):
        """check for commentString on start of line
           return 0 or 1
        """
        if self.dollar[0].startswith( commentString ):
            return 1
        return 0

    def isEmpty( self ):
        return (self.NF == 0)
#
#==============================================================================
#

