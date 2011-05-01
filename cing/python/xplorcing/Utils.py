'''
Created on Apr 28, 2011

@author: jd
'''
from random import randint
from random import seed
from xplorSimulation import getXplorSimulation
import time

def getRandomSeed(size=6):
    """Silly code. Get a random alphanumeric int of a given size"""
    NUMERIC = [chr(x) for x in range(48, 58)]
    n = len(NUMERIC) - 1
    seed(time.time()*time.time())
    resultStr = ''.join([NUMERIC[randint(0, n)] for x in range(size)])
    result = int(resultStr)
    return result
# end def

def addIon(sel):
    """
    Modeled after psfGen#addDisulfideBond

    Add an ion

    Should be called after PSF information is generated.
    """

    from atomSel import AtomSel

    if isinstance(sel,str):
        sel = AtomSel(sel)

    xSim = getXplorSimulation(sel.simulation())
    xSim.command("""patch
                       DISU reference=1=( segid "%s" and resid %d )
                            reference=2=( segid "%s" and resid %d )
                     end""" % (sel[0].segmentName(),sel[0].residueNum()))

    return
# end def
