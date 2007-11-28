from cing.Libs.NTutils import NTlist
import math

def peirceTest( valueList ):
    """Perform a peirce test for outliers.
       2 < len( valueList ) <= 60
       
       Return a tuple of two NTlists:
        (newValues, outliers)
        
       Based upon:
           Ross, S.M., "Peirce's criterion for the elimination of suspect 
           experimental data" J. Engineering Technology, 2003
       
       AWSS: since it's limited to 60 elements, now valueList is break down in 
             lists of 60 elements (if less, no problem), and if there's reminder
             from len(valueList) % 60, then a list with the last 60 elements is
             appended to listOfnewValues. So a pierceTest is done over each list
             of 60 elements and newValues and outliers list are updated 
             accordingly.
    """

    peirce = {}
#
# PEIRCE'S CRITERION TABLE, R; ONE MEASURED QUANTITY
#
#  Total observations
#                 Number of doubtful observations
#                 1      2      3      4      5      6      7      8      9
    peirce[3]  = [1.196]
    peirce[4]  = [1.383, 1.078]
    peirce[5]  = [1.509, 1.200]
    peirce[6]  = [1.610, 1.299, 1.099]
    peirce[7]  = [1.693, 1.382, 1.187, 1.022]
    peirce[8]  = [1.763, 1.453, 1.261, 1.109]
    peirce[9]  = [1.824, 1.515, 1.324, 1.178, 1.045]
    peirce[10] = [1.878, 1.570, 1.380, 1.237, 1.114]
    peirce[11] = [1.925, 1.619, 1.430, 1.289, 1.172, 1.059]
    peirce[12] = [1.969, 1.883, 1.475, 1.336, 1.221, 1.118, 1.009]
    peirce[13] = [2.007, 1.704, 1.516, 1.379, 1.266, 1.167, 1.070]
    peirce[14] = [2.043, 1.741, 1.554, 1.417, 1.307, 1.210, 1.120, 1.026]
    peirce[15] = [2.076, 1.775, 1.889, 1.453, 1.344, 1.249, 1.164, 1.078]
    peirce[16] = [2.106, 1.807, 1.622, 1.486, 1.378, 1.285, 1.202, 1.122, 1.039]
    peirce[17] = [2.134, 1.836, 1.652, 1.517, 1.409, 1.318, 1.237, 1.161, 1.084]
    peirce[18] = [2.161, 1.364, 1.680, 1.546, 1.438, 1.348, 1.268, 1.195, 1.123]
    peirce[19] = [2.185, 1.890, 1.707, 1.573, 1.466, 1.377, 1.298, 1.228, 1.158]
    peirce[20] = [2.209, 1.914, 1.732, 1.599, 1.492, 1.404, 1.326, 1.255, 1.190]
    peirce[21] = [2.230, 1.938, 1.756, 1.623, 1.517, 1.429, 1.352, 1.282, 1.218]
    peirce[22] = [2.251, 1.960, 1.779, 1.646, 1.540, 1.452, 1.376, 1.308, 1.245]
    peirce[23] = [2.271, 1.981, 1.800, 1.668, 1.563, 1.475, 1.399, 1.332, 1.270]
    peirce[24] = [2.290, 2.000, 1.821, 1.689, 1.584, 1.497, 1.421, 1.354, 1.293]
    peirce[25] = [2.307, 2.019, 1.840, 1.709, 1.604, 1.517, 1.442, 1.375, 1.315]
    peirce[26] = [2.324, 2.037, 1.859, 1.728, 1.624, 1.537, 1.462, 1.396, 1.336]
    peirce[27] = [2.341, 2.055, 1.877, 1.746, 1.642, 1.556, 1.481, 1.415, 1.356]
    peirce[28] = [2.356, 2.071, 1.894, 1.764, 1.660, 1.574, 1.500, 1.434, 1.375]
    peirce[29] = [2.371, 2.088, 1.911, 1.781, 1.677, 1.591, 1.517, 1.452, 1.393]
    peirce[30] = [2.385, 2.103, 1.927, 1.797, 1.694, 1.608, 1.534, 1.469, 1.411]
    peirce[31] = [2.399, 2.118, 1.942, 1.812, 1.710, 1.624, 1.550, 1.486, 1.428]
    peirce[32] = [2.412, 2.132, 1.957, 1.828, 1.725, 1.640, 1.567, 1.502, 1.444]
    peirce[33] = [2.425, 2.146, 1.971, 1.842, 1.740, 1.655, 1.582, 1.517, 1.459]
    peirce[34] = [2.438, 2.159, 1.985, 1.856, 1.754, 1.669, 1.597, 1.532, 1.475]
    peirce[35] = [2.450, 2.172, 1.998, 1.870, 1.768, 1.683, 1.611, 1.547, 1.489]
    peirce[36] = [2.461, 2.184, 2.011, 1.883, 1.782, 1.697, 1.624, 1.561, 1.504]
    peirce[37] = [2.472, 2.196, 2.024, 1.896, 1.795, 1.711, 1.638, 1.574, 1.517]
    peirce[38] = [2.483, 2.208, 2.036, 1.909, 1.807, 1.723, 1.651, 1.587, 1.531]
    peirce[39] = [2.494, 2.219, 2.047, 1.921, 1.820, 1.736, 1.664, 1.600, 1.544]
    peirce[40] = [2.504, 2.230, 2.059, 1.932, 1.832, 1.748, 1.676, 1.613, 1.556]
    peirce[41] = [2.514, 2.241, 2.070, 1.944, 1.843, 1.760, 1.688, 1.625, 1.568]
    peirce[42] = [2.524, 2.251, 2.081, 1.955, 1.855, 1.771, 1.699, 1.636, 1.580]
    peirce[43] = [2.533, 2.261, 2.092, 1.966, 1.866, 1.783, 1.711, 1.648, 1.592]
    peirce[44] = [2.542, 2.271, 2.102, 1.976, 1.876, 1.794, 1.722, 1.659, 1.603]
    peirce[45] = [2.551, 2.281, 2.112, 1.987, 1.887, 1.804, 1.733, 1.670, 1.614]
    peirce[46] = [2.560, 2.290, 2.122, 1.997, 1.897, 1.815, 1.743, 1.681, 1.625]
    peirce[47] = [2.568, 2.299, 2.131, 2.006, 1.907, 1.825, 1.754, 1.691, 1.636]
    peirce[48] = [2.577, 2.308, 2.140, 2.016, 1.917, 1.835, 1.764, 1.701, 1.646]
    peirce[49] = [2.585, 2.317, 2.149, 2.026, 1.927, 1.844, 1.773, 1.711, 1.656]
    peirce[50] = [2.592, 2.326, 2.158, 2.035, 1.936, 1.854, 1.783, 1.721, 1.666]
    peirce[51] = [2.600, 2.334, 2.167, 2.044, 1.945, 1.863, 1.792, 1.730, 1.675]
    peirce[52] = [2.608, 2.342, 2.175, 2.052, 1.954, 1.872, 1.802, 1.740, 1.685]
    peirce[53] = [2.615, 2.350, 2.184, 2.061, 1.963, 1.881, 1.811, 1.749, 1.694]
    peirce[54] = [2.622, 2.358, 2.192, 2.069, 1.972, 1.890, 1.820, 1.758, 1.703]
    peirce[55] = [2.629, 2.365, 2.200, 2.077, 1.980, 1.898, 1.828, 1.767, 1.711]
    peirce[56] = [2.636, 2.373, 2.207, 2.085, 1.988, 1.907, 1.837, 1.775, 1.720]
    peirce[57] = [2.643, 2.380, 2.215, 2.093, 1.996, 1.915, 1.845, 1.784, 1.729]
    peirce[58] = [2.650, 2.387, 2.223, 2.101, 2.004, 1.923, 1.853, 1.792, 1.737]
    peirce[59] = [2.656, 2.394, 2.230, 2.109, 2.012, 1.931, 1.861, 1.800, 1.745]
    peirce[60] = [2.663, 2.401, 2.237, 2.116, 2.019, 1.939, 1.869, 1.808, 1.753]
    
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
        newValuesList.average(byItem=1)
        newL = len(newValuesList)
        notDone   = True
        nOutliers = 0
        while notDone and nOutliers < len( peirce[newL] ):
            R = peirce[newL][nOutliers]
            maxDeviation = R * newValuesList.sd
            n = 0
            for item in newValuesList:
                i,v = item
                if ( math.fabs( v-newValuesList.av ) > maxDeviation ):
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


#-----------------------------------------------------------------------------
# Testing from here-on
#-----------------------------------------------------------------------------
#
if __name__ == '__main__':
    pass
    values = [101.2, 90.0, 99.0, 102.0, 103.0, 100.2, 89.0, 98.1, 101.5, 102.0]
    v,o = peirceTest( values )
    print 'v=',v
    print v.av, v.sd
    print 'o=',o
    
