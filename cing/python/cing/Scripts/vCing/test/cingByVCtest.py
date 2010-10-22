#!/usr/bin/env python
# Execute like:
# $CINGROOT/python/cing/Scripts/vCing/test/cingByVCtest.py a b

from cing import header
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.main import getStartMessage
from cing.main import getStopMessage


if __name__ == "__main__":
    cing.verbosity = verbosityDebug

    NTmessage(header)
    NTmessage(getStartMessage())

    NTmessage("Starting program: %s" % sys.argv[0])
    NTdebug("Argument retrieved: %s" % str(sys.argv[1:] ))

    NTmessage(getStopMessage())