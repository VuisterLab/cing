from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTwarning
import math
TWO_PI = 2. * math.pi

#A small angle (in degrees/rads) that is used to determine real differences. */
ANGLE_EPSILON = 1.e-10

def violationAngle(value, lowerBound, upperBound):
#  Original code might have been correct too but JFD preferred to work with
#  tested code  from Wattos set to Python. Nothing wrong with this code though.
#    l = NTlist(self.lower, self.upper, d)
#    l.limit(self.lower, self.lower+360.0) # list circular with lower as lowest value
#    h = NTlist(self.lower, self.upper, d) # list circular with upper as highest value
#    h.limit(self.upper-360, self.upper)
#    if l[0]<=l[2] and l[2]<=l[1]: # between lower and upper
#        self.violations.append( 0.0 )
#    else: # there is a violation
#        if math.fabs(l[2]-l[1]) < math.fabs( h[2]-h[0] ): # find smallest to either upper or lower bound
#            v = l[2]-l[1]
#        else:
#            v = h[2]-h[0]
#        fv = math.fabs(v)
###############################################################
        # operate in float space (not integer)
#        value      -= .0
        "Return None on error"
        if lowerBound == None: # See entry 1bn0
            NTwarning("Lower bound is None; skipping this angle for this model.")
            return
        if upperBound == None: # See entry 1bn0
            NTwarning("Upper bound is None; skipping this angle for this model.")
            return
        lowerBound -= .0 # only one needed because see below.
#        upperBound -= .0
        
        upperBound -= lowerBound
        value      -= lowerBound
        upperBound = to_0_360(upperBound)
        value      = to_0_360(value)
#//        lowerBound = 0; not used

#        // Upperbound violation in range [0,2pi>
        dU = value-upperBound;
        if dU <= 0.:
            return 0.
#        // Lowerbound violation in range <0,2pi>
        dL = 360. - value

#        // Here's the funny part, even though dU and dL can be up to 2pi
#        // the smallest of the 2 is always only up to pi.
#        // minViol in [0,pi]
        min_viol = min(dU, dL)
        return min_viol


def to_0_2pi( a ):
    while a >= TWO_PI:
        a -= TWO_PI
    while a < 0.:
        a += TWO_PI
    return a  

def to_0_360( a ):
    while a >= 360.:
        a -= 360.
    while a < 0.:
        a += 360.
    return a  


    