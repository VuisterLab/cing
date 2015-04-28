#!/usr/bin/env python
# Execute like:
# $CINGROOT/python/cing/Scripts/vCing/test/cingByVCtest.py a b

import cing
from cing.Libs.NTutils import * #@UnusedWildImport


if __name__ == "__main__":
    cing.verbosity = verbosityDebug

    nTmessage(cing.cingDefinitions.getHeaderString())
    nTmessage(cing.systemDefinitions.getStartMessage())

    nTmessage("Starting program: %s" % sys.argv[0])
    nTdebug("Argument retrieved: %s" % str(sys.argv[1:] ))

    nTmessage(cing.systemDefinitions.getStopMessage())