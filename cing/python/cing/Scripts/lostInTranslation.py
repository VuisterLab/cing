# -*- coding: utf-8 -*-
# the above just reminds to the fact that the properties files are all utf-8 encoded.
# Note that eclipse stores the utf-8 nature of resources in:
# .settings/org.eclipse.core.resources.prefs
from cing.Libs.NTutils import * #@UnusedWildImport
from glob import glob
import codecs


class lostInTranslation():
    """Find the missing phrases in each language iCing tries to support"""

    def __init__(self):
#        self.i18nDir = "java/src/cing/client"
        self.i18nDir = "src/cing/client/i18n"
        self.lostInTranslationDir = "../lostInTranslation"
        "Relative to the self.i18nDir"
        absPathGwtDir = os.path.join(cing.cingRoot, self.i18nDir )
        if os.chdir(absPathGwtDir):
            nTerror("Failed to change to directory: "+absPathGwtDir)
            sys.exit(1)

    def findPhrases(self):
#        CINGROOT = os.getenv("CINGROOT", "/Users/jd/workspace35/cing") # default value should not be used...
        propList  = glob( 'iCingConstants_*.properties')
        nTmessage("Found propList [" + `len(propList)` + "] "  + `propList`)
        propBaseFile = os.path.join( 'iCingConstants.properties' )
        propBaseMap = self.getPropMap( propBaseFile )
        nTmessage ( `propBaseMap` )
        for propFile in propList:
            n = len(propFile)
#            iCingConstants_XX.properties
#                                       n
            countryCode = propFile[n-13:n-11]
            fileTodo = 'iCingConstants-%2s-todo.properties' %  countryCode
            fileTodo = os.path.join( self.lostInTranslationDir, fileTodo )
            nf = codecs.open( fileTodo, "w", "utf-8" )
            nTmessage("Writing to file: " + fileTodo)
            propMap = self.getPropMap( propFile )
            nTmessage("Found propBase [" + `len(propMap)` + "] "  + `propMap`)
            keyList = propBaseMap.keys()
            keyList.sort()
            for key in keyList:
                if key in propMap:
                    continue
                value = propBaseMap[key]
                # All that's written needs to be unicode.
                nf.write( u"%-20s = " % key )
                nf.write( value ) # might be utf-8
                nf.write( u"\n" ) # might be utf-8
#                nTmessage("Lost: " + key)
            nf.close()

    def getPropMap( self, propBaseFile ):
        f = codecs.open( propBaseFile, "r", "utf-8" )
        # now the reads will result in unicode being returned.
        r={}
        lineNo = 0
        for line in f:
            lineNo += 1
            if line == "":
                continue
#            nTdebug("line: " + line)
            try:
                (key,value) = line.split('=')
            except :
                nTerror("In file [%s] on line [%d]: [%s]" % (propBaseFile, lineNo, line))
                raise # re-raise the current exception (new in 1.5)

            key = key.strip()
            value = value.strip()
            r[key]=value
        return r



if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
    lit = lostInTranslation()
    lit.findPhrases()