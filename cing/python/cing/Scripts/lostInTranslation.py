# -*- coding: utf-8 -*-
# the above just reminds to the fact that the properties files are all utf-8 encoded.
# Note that eclipse stores the utf-8 nature of resources in:
# .settings/org.eclipse.core.resources.prefs
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from glob import glob
import cing
import os
import sys
import codecs


class lostInTranslation():
    """Find the missing phrases in each language iCing tries to support"""

    def __init__(self):
        self.gwtDir = "java/src/cing/client"
        absPathGwtDir = os.path.join(cing.cingRoot, self.gwtDir )
        if os.chdir(absPathGwtDir):
            NTerror("Failed to change to directory: "+absPathGwtDir)
            sys.exit(1)
    
    def findPhrases(self):
#        CINGROOT = os.getenv("CINGROOT", "/Users/jd/workspace34/cing") # default value should not be used...
        propList  = glob( 'iCingConstants_*.properties') 
        NTmessage("Found propList [" + `len(propList)` + "] "  + `propList`)
        propBaseFile = os.path.join( 'iCingConstants.properties' )
        propBaseMap = self.getPropMap( propBaseFile )
        NTmessage ( `propBaseMap` )
        for propFile in propList:
            n = len(propFile)
#            iCingConstants_XX.properties
#                                       n
            countryCode = propFile[n-13:n-11]
            fileTodo = 'iCingConstants-%2s-todo.properties' %  countryCode
            nf = codecs.open( fileTodo, "w", "utf-8" )
            NTmessage("Writing to file: " + fileTodo)
            propMap = self.getPropMap( propFile )
            NTmessage("Found propBase [" + `len(propMap)` + "] "  + `propMap`)
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
#                NTmessage("Lost: " + key)
            nf.close()
                
    def getPropMap( self, propBaseFile ):
        f = codecs.open( propBaseFile, "r", "utf-8" )
        # now the reads will result in unicode being returned.        
        r={}
        for line in f:
            (key,value) = line.split('=')
            key = key.strip()
            value = value.strip()
            r[key]=value
        return r
        
            

if __name__ == '__main__':
    lit = lostInTranslation()
    lit.findPhrases()