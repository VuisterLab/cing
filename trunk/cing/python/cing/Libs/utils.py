"""
Utilities routines; new for V3
"""
__author__ = 'geerten'


def compareVersions(version1, version2):
    """
    Compare version1 with version2
    can compare strings and ints;

    return -1 if version1 is older then version2
    return 0 if version1 == version 2
    return 1 if version1 is newer than version2

    '1.0.1' older than '2.0.0'
    '2.1.1' newer than  0.95
     0.94   older than  0.95
    '0.93'  older than  0.95

    """

    # convert to list of ints
    version1 = map(int, str(version1).split('.'))
    version2 = map(int, str(version2).split('.'))

    i = 0
    while i<len(version1) and i<len(version2):
        if version1[i] < version2[i]: return -1
        if version1[i] > version2[i]: return 1
        i += 1
    #end while

    #apparently, identical up to now, but still can be unequal length's
    if len(version1) < len(version2): return -1
    if len(version1) > len(version2): return 1

    # they are the same
    return 0
#end if