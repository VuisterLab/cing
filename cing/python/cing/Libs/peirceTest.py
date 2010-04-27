from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTdebug
import math


"""
    Perform a Peirce test for outliers.
    2 < len( valueList ) <= 60

    Based upon:
        Ross, S.M., "Peirce's criterion for the elimination of suspect
        experimental data" J. Engineering Technology, 2003

    AWSS: since it's limited to 60 elements, now valueList breaks down in
        lists of 60 elements (if less, no problem), and if there's remainder
        from len(valueList) % 60, then a list with the last 60 elements is
        appended to listOfnewValues. So a pierceTest is done over each list
        of 60 elements and newValues and outliers list are updated
        accordingly.

    JFD: I think the previous workaround for the lack of Peirce data beyond
        the 60th element should be improved. In the previous workaround it
        could happen that a small sublist gets analyzed and an
        item would not be identified as a outlier whereas it would if it
        was considered in the scope of the full list.
        Since the shape of the items are so monotonous a simple extrapolation
        was implemented.

        Let the "Number of doubtful observations" be called y and the number of
        total observations is called x.

        A- R[x][y] is approximately 1 sigma at the right hand side of the table.
            R[x][y] for when y>9 is simply estimated to be R[x][9] - (y-9)*delta(x).
            with delta(x) defined such that R[x][x/2]=1.
            Only extend the table on the right to have x/2 number of columns.
            x/2 is less wide than the first rows suggest. Extending the table
            only starts at row 20.
        B- R[x][y] can be estimated to be R[60][y] for x over 60. This results in
            only slightly fewer outliers to be identified than when the serie
            would be correctly expanded.
            E.g. when x = 10E6 R[10E6][1] is equated to R[60][1] (2.663)
        C- For calculating the missing values such as R[10E6][10E2] the above
            is combined.

        Obviously, also this workaround might report less outliers but it will
        report more than the first workaround as higher R's are used.
"""
class Peirce:
    def __init__(self):
        #
        # PEIRCE'S CRITERION TABLE, R; ONE MEASURED QUANTITY
        #
        #  Total observations
        #  Number of doubtful observations
        #  1      2      3      4      5      6      7      8      9
        self.peirce = [
        [],   # 0
        [],   # 1
        [],   # 2
        [1.196]                                                          , #3
        [1.383, 1.078]                                                   ,
        [1.509, 1.200]                                                   , #5
        [1.610, 1.299, 1.099]                                            ,
        [1.693, 1.382, 1.187, 1.022]                                     ,
        [1.763, 1.453, 1.261, 1.109]                                     ,
        [1.824, 1.515, 1.324, 1.178, 1.045]                              ,
        [1.878, 1.570, 1.380, 1.237, 1.114]                              , #10
        [1.925, 1.619, 1.430, 1.289, 1.172, 1.059]                       ,
        [1.969, 1.883, 1.475, 1.336, 1.221, 1.118, 1.009]                ,
        [2.007, 1.704, 1.516, 1.379, 1.266, 1.167, 1.070]                ,
        [2.043, 1.741, 1.554, 1.417, 1.307, 1.210, 1.120, 1.026]         ,
        [2.076, 1.775, 1.889, 1.453, 1.344, 1.249, 1.164, 1.078]         , #15
        [2.106, 1.807, 1.622, 1.486, 1.378, 1.285, 1.202, 1.122, 1.039]  , #16
        [2.134, 1.836, 1.652, 1.517, 1.409, 1.318, 1.237, 1.161, 1.084]  ,
        [2.161, 1.364, 1.680, 1.546, 1.438, 1.348, 1.268, 1.195, 1.123]  , #18
        [2.185, 1.890, 1.707, 1.573, 1.466, 1.377, 1.298, 1.228, 1.158]  ,
        [2.209, 1.914, 1.732, 1.599, 1.492, 1.404, 1.326, 1.255, 1.190]  , #20
        [2.230, 1.938, 1.756, 1.623, 1.517, 1.429, 1.352, 1.282, 1.218]  ,
        [2.251, 1.960, 1.779, 1.646, 1.540, 1.452, 1.376, 1.308, 1.245]  ,
        [2.271, 1.981, 1.800, 1.668, 1.563, 1.475, 1.399, 1.332, 1.270]  ,
        [2.290, 2.000, 1.821, 1.689, 1.584, 1.497, 1.421, 1.354, 1.293]  ,
        [2.307, 2.019, 1.840, 1.709, 1.604, 1.517, 1.442, 1.375, 1.315]  ,
        [2.324, 2.037, 1.859, 1.728, 1.624, 1.537, 1.462, 1.396, 1.336]  ,
        [2.341, 2.055, 1.877, 1.746, 1.642, 1.556, 1.481, 1.415, 1.356]  ,
        [2.356, 2.071, 1.894, 1.764, 1.660, 1.574, 1.500, 1.434, 1.375]  ,
        [2.371, 2.088, 1.911, 1.781, 1.677, 1.591, 1.517, 1.452, 1.393]  ,
        [2.385, 2.103, 1.927, 1.797, 1.694, 1.608, 1.534, 1.469, 1.411]  ,
        [2.399, 2.118, 1.942, 1.812, 1.710, 1.624, 1.550, 1.486, 1.428]  ,
        [2.412, 2.132, 1.957, 1.828, 1.725, 1.640, 1.567, 1.502, 1.444]  ,
        [2.425, 2.146, 1.971, 1.842, 1.740, 1.655, 1.582, 1.517, 1.459]  ,
        [2.438, 2.159, 1.985, 1.856, 1.754, 1.669, 1.597, 1.532, 1.475]  ,
        [2.450, 2.172, 1.998, 1.870, 1.768, 1.683, 1.611, 1.547, 1.489]  ,
        [2.461, 2.184, 2.011, 1.883, 1.782, 1.697, 1.624, 1.561, 1.504]  ,
        [2.472, 2.196, 2.024, 1.896, 1.795, 1.711, 1.638, 1.574, 1.517]  ,
        [2.483, 2.208, 2.036, 1.909, 1.807, 1.723, 1.651, 1.587, 1.531]  ,
        [2.494, 2.219, 2.047, 1.921, 1.820, 1.736, 1.664, 1.600, 1.544]  ,
        [2.504, 2.230, 2.059, 1.932, 1.832, 1.748, 1.676, 1.613, 1.556]  ,
        [2.514, 2.241, 2.070, 1.944, 1.843, 1.760, 1.688, 1.625, 1.568]  ,
        [2.524, 2.251, 2.081, 1.955, 1.855, 1.771, 1.699, 1.636, 1.580]  ,
        [2.533, 2.261, 2.092, 1.966, 1.866, 1.783, 1.711, 1.648, 1.592]  ,
        [2.542, 2.271, 2.102, 1.976, 1.876, 1.794, 1.722, 1.659, 1.603]  ,
        [2.551, 2.281, 2.112, 1.987, 1.887, 1.804, 1.733, 1.670, 1.614]  ,
        [2.560, 2.290, 2.122, 1.997, 1.897, 1.815, 1.743, 1.681, 1.625]  ,
        [2.568, 2.299, 2.131, 2.006, 1.907, 1.825, 1.754, 1.691, 1.636]  ,
        [2.577, 2.308, 2.140, 2.016, 1.917, 1.835, 1.764, 1.701, 1.646]  ,
        [2.585, 2.317, 2.149, 2.026, 1.927, 1.844, 1.773, 1.711, 1.656]  ,
        [2.592, 2.326, 2.158, 2.035, 1.936, 1.854, 1.783, 1.721, 1.666]  ,
        [2.600, 2.334, 2.167, 2.044, 1.945, 1.863, 1.792, 1.730, 1.675]  ,
        [2.608, 2.342, 2.175, 2.052, 1.954, 1.872, 1.802, 1.740, 1.685]  ,
        [2.615, 2.350, 2.184, 2.061, 1.963, 1.881, 1.811, 1.749, 1.694]  ,
        [2.622, 2.358, 2.192, 2.069, 1.972, 1.890, 1.820, 1.758, 1.703]  ,
        [2.629, 2.365, 2.200, 2.077, 1.980, 1.898, 1.828, 1.767, 1.711]  ,
        [2.636, 2.373, 2.207, 2.085, 1.988, 1.907, 1.837, 1.775, 1.720]  ,
        [2.643, 2.380, 2.215, 2.093, 1.996, 1.915, 1.845, 1.784, 1.729]  ,
        [2.650, 2.387, 2.223, 2.101, 2.004, 1.923, 1.853, 1.792, 1.737]  ,
        [2.656, 2.394, 2.230, 2.109, 2.012, 1.931, 1.861, 1.800, 1.745]  ,
        [2.663, 2.401, 2.237, 2.116, 2.019, 1.939, 1.869, 1.808, 1.753]  ,
        ]
        self.peirceLength = len(self.peirce)-1 # 60

    def _getR(self,x,y):
        'May not be called by x<3, returns None if y >= x-2.'
        if x < 3:
            return None

        # Simple things first; does it fall within the paper's table.
        row = x
        if x>self.peirceLength:
            row = self.peirceLength
        if y<=len(self.peirce[row]):
            return self.peirce[row][y-1]

        if row < 20: # dont extend the width before this.
            return self.peirce[row][-1]

        # At this point the row,y combination falls to the right of the table
        # row>=20 and we need delta to get an R value close to 1.
        if y >= x/2:
            NTdebug("Cing was trying to remove from a set of "+`x`+" values an unexpected high number of outliers: "+`y`+" this is impossible")
            return None

        lastValue = self.peirce[row][-1]
        maxWidth = x/2
        delta = (lastValue - 1.)/(maxWidth-9) # float semantics needs to be enforced.
        R = lastValue - (y-9)*delta
#        NTdebug("delta: "+`delta`)
#        NTdebug("R    : "+`R`)
        return R




    def peirceTestOld( self, valueList ):
        l = len( valueList )

        if l<3: return (None, None)

        newValues = NTlist()
        outliers  = NTlist()

        i = 0
        for v in valueList:
            newValues.append( [i,v] )
            i += 1
        #end for

        ngroups, reminder = l / 60, l % 60

        listOfnewValues = []

        if ngroups == 0:
            listOfnewValues = [newValues]
        else:
            for ngroup in range(ngroups):
                listOfnewValues.append(newValues[ngroup*60:(ngroup+1)*60])
            if reminder:
                listOfnewValues.append(newValues[-60:])

        #newValues.sort() #Why sort?
        #newValues.average(byItem=1)

        for newValuesList in listOfnewValues:
#            NTdebug(newValuesList)
            newValuesList.average(byItem=1)
#            NTdebug("av: " + `newValuesList.av`)
#            NTdebug("sd: " + `newValuesList.sd`)
            newL = len(newValuesList)
            notDone   = True
            nOutliers = 0
            while notDone and nOutliers < len( self.peirce[newL] ):
                R = self.peirce[newL][nOutliers]
#                NTdebug("nOutliers: "+ `nOutliers` )
#                NTdebug("R        : "+ `R`)
                maxDeviation = R * newValuesList.sd
                n = 0
                for item in newValuesList:
                    i,v = item
                    if ( math.fabs( v-newValuesList.av ) > maxDeviation ):
#                        NTdebug("Removing item: " + `i` + ", " + `v`)
                        try:
                            newValues.remove( item )
                            outliers.append( item )
                        except: pass
                        #end try
                        nOutliers += 1
                        n += 1
                    #end if
                #end for
                notDone = (n>0)
            #end while

        newValues.average(byItem=1)
        return (newValues,outliers)
    #end def


    def peirceTest( self, valueList ):
        """Return a tuple of two NTlists:    (newValues, outliers). The newvalues NTlist
        contains elements that are the index and the value at that index. The outliers NTlist
        contains the same.
            Input data is not modified by this routine. Input is of type NTlist.
            Returns None on error.
            When called with less than 3 values returns all those values as expected.
            (Used to return (None, None) on error.)
        """
        x = len( valueList )


        newValues = NTlist()
        outliers  = NTlist()

        i = 0
        for v in valueList:
            newValues.append( [i,v] )
            i += 1

        y = len(outliers) # Number of outliers is zero to start with
        newValues.average(byItem=1)
        sd = newValues.sd # not to be changed until the end.
        av = newValues.av # not to be changed until the end.
#        NTdebug("av: " + `av`)
#        NTdebug("sd: " + `sd`)

        if x<3:
#            NTdebug("Peirce test called with less than 3 values.")
#            NTdebug("For less than 3 values no outliers can be identified by this methodology")
            return (newValues, outliers)

        done = False # At least give it a try.
        while not done:
            done = True # Quit if no outliers were identified.
            R = self._getR(x, y)
            if not R:
#                NTdebug("Failed to get a Peirce constant R; not adding outliers anymore.")
#                NTdebug('This happened on values:\n%s' % valueList)
#                return None
                break
            maxDeviation = R * sd
#            NTdebug("R : " + `R`)
#            NTdebug("md: " + `maxDeviation`)

            c = len(newValues)-1 # Start at the end of the list because deletions in lists are easiest (optimal) that way.
            while c>=0:
                item = newValues[c]
                i,v = item
                if ( math.fabs( v-av ) > maxDeviation ):
#                    NTdebug("Removing: " + `i` + "," + `v`)
                    del newValues[ c ]
                    outliers.append( item )
                    y = len(outliers) # Keep it simple.
                    done = False # Try another R value later.
                c -= 1

        newValues.average(byItem=1)
        return (newValues,outliers)
    #end def

# A bit of ugly object oriented programming follows to accomodate legacy way of handling.
p = Peirce()
def peirceTest(valueList):
    return p.peirceTest(valueList)
def peirceTestOld(valueList):
    return p.peirceTestOld(valueList)

# Testing is now done in standard test setup; see test dir.
