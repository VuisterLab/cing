#!/usr/bin/env python
#@PydevCodeAnalysisIgnore # pylint: disable-all

# ADD QUEEN SOURCE TO SYSTEM PATH
import sys,os

sys.path += [os.path.join(sys.path[0],'src/py'),
             os.path.join(sys.path[0],'src/c'),
             os.path.join(sys.path[0],'src/3rd-party')]

print " Note: commands of generate.py are now contained in queen.py"
print " Type queen --help for info"

