from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqDssp import * #@UnusedWildImport
from cing.PluginCode.required.reqProcheck import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.constants import * #@UnusedWildImport

dpi=72.27 # Latex definition
inches_per_pt = 1./dpi
golden_mean = (math.sqrt(5.)-1.)/2.     # Aesthetic ratio where possible.
DEFAULT_FONT_SIZE = 12

KEY_LIST_STR = 'keyList'
KEY_LIST2_STR = 'keyList2'
KEY_LIST3_STR = 'keyList3'
KEY_LIST4_STR = 'keyList4'
KEY_LIST5_STR = 'keyList5'

XLABEL_STR = 'xLabel'
YLABEL_STR = 'yLabel'
USE_ZERO_FOR_MIN_VALUE_STR = 'useZeroForMinValue'
USE_VERBOSE_Y_LOCATOR_STR = 'useVerboseYLocator' # Potentially more than the default 10 major ticks on Y axis.
USE_MIN_VALUE_STR = 'useMinValue'
USE_MAX_VALUE_STR = 'useMaxValue'
USE_ROG_FOR_COLOR_STR = 'useRogForColor'

NT_MOLECULE_PLOT_IDX_X_VALUE = 0
NT_MOLECULE_PLOT_IDX_VALUE_LIST = 1
NT_MOLECULE_PLOT_IDX_ROG_COLOR = 2

def nTplotAttributes( **kwds ):
    a = NTdict()

    a.__FORMAT__ =    '=== plotting attributes ===\n' +\
                      'lineType:   %(lineType)s\n' +\
                      'lineWidth:  %(lineWidth).1f\n' +\
                      'lineColor:  %(lineColor)s\n' +\
                      'fill:       %(fill)s\n' +\
                      'line:       %(line)s\n' +\
                      'fillColor:  %(fillColor)s\n' +\
                      'pointType:  %(pointType)s\n' +\
                      'pointSize:  %(pointSize).1f\n' +\
                      'pointColor: %(pointColor)s\n' +\
                      'font:       %(font)s\n' +\
                      'fontSize:   %(fontSize)d\n' +\
                      'fontColor:  %(fontColor)s\n' +\
                      'rotation:   %(rotation)s\n' +\
                      'verticalalignment:    %(verticalalignment)s\n' +\
                      'horizontalalignment:  %(horizontalalignment)s\n'

    # line defaults
    a.lineType   = 'solid'
    a.lineColor  = 'black'
    a.lineWidth  = 1.0

    # box
    a.fill       = True
    a.fillColor  = 'black'
    a.line       = False

    # points
    a.pointType  = None   # in matplotlib: marker
    a.pointSize  = 2.0    # in matplotlib: markeredgewidth
    a.pointColor = 'blue' # in matplotlib: markeredgecolor

    # fonts
    a.font       = 'Helvetica'
    a.fontSize   = DEFAULT_FONT_SIZE
    a.fontColor  = 'black'

    # text
    a.verticalalignment   = 'bottom' # [ 'center' | 'top' | 'bottom' ]
    a.horizontalalignment = 'left' # right or center
    a.rotation            = 'horizontal' # angle in degrees 'vertical' | 'horizontal'

    a.alpha = 1. # Takes a value in resList [0,1] for transparency/blending.

    # update
    a.update( kwds )

    return a
#end def

def lineAttributes( type='solid', width=1.0, color='black', alpha=1. ):
    return nTplotAttributes( lineType=type, lineWidth=width, lineColor=color, alpha=alpha )
#end def

def boxAttributes( fill=True, fillColor='black', line=False, lineColor='black', alpha=1. ):
    return nTplotAttributes( lineType='solid', lineColor=lineColor, line=line,
                             fill=fill, fillColor=fillColor, alpha=alpha
                           )
#end def

def fontAttributes( font='Helvetica', size=DEFAULT_FONT_SIZE, color='black', alpha=1. ):
    return nTplotAttributes( font=font, fontSize=size, fontColor=color, alpha=alpha )
#end def

def fontVerticalAttributes( horizontalalignment='left', verticalalignment  = 'center', rotation   = 'vertical', size=DEFAULT_FONT_SIZE ):
    result = fontAttributes(size=size)
    result.horizontalalignment=horizontalalignment
    result.verticalalignment=verticalalignment
    result.rotation=rotation
    return result

def pointAttributes( type='circle', size=4.0, pointEdgeWidth=2.0, color='black', alpha=1. ):
    return nTplotAttributes( pointType=type, pointSize=size, pointEdgeWidth=pointEdgeWidth, pointColor=color, alpha=alpha )
#end def

# Some default attributes
defaultAttributes  = nTplotAttributes()

SOLID_LINE_TYPE = 'solid'
DOTTED_LINE_TYPE = 'dotted'
LONGDASHED_LINE_TYPE = 'longdashed'
DASHDOT_LINE_TYPE = 'dash-dot'
NONE_LINE_TYPE = 'None'

cingLineTypeList = [ SOLID_LINE_TYPE, DOTTED_LINE_TYPE, LONGDASHED_LINE_TYPE, DASHDOT_LINE_TYPE, NONE_LINE_TYPE]

solidLine          = lineAttributes( type=SOLID_LINE_TYPE,      width=1.0, color='black' )
dottedLine         = lineAttributes( type=DOTTED_LINE_TYPE,     width=1.0, color='black' )
dashedline         = lineAttributes( type=LONGDASHED_LINE_TYPE, width=1.0, color='black' )
dashdotline        = lineAttributes( type=DASHDOT_LINE_TYPE,    width=1.0, color='black' )
noneline           = lineAttributes( type=NONE_LINE_TYPE,       width=1.0, color='black' )
redLine            = lineAttributes( type='solid',      width=1.0, color='red' )
blueLine           = lineAttributes( type='solid',      width=1.0, color='blue' )
greenLine          = lineAttributes( type='solid',      width=1.0, color='green' )

blackBox           = boxAttributes( fill=True,  fillColor='black' )
redBox             = boxAttributes( fill=True,  fillColor='red' )
greenBox           = boxAttributes( fill=True,  fillColor='green' )
openBox            = boxAttributes( fill=False, fillColor='black', line=True, lineColor='black' )

plusPoint          = pointAttributes( type='plus',          size=2.0, color='blue' )
circlePoint        = pointAttributes( type='circle',        size=2.0, color='blue' )


#-----------------------------------------------------------------------------
# Color conversions
# These functions, when given a magnitude mag between cmin and cmax, return
# a colour tuple (red, green, blue). Light blue is cold (low magnitude)
# and yellow is hot (high magnitude).
#
# GV: Adapted from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52273
#
#-----------------------------------------------------------------------------

def floatRgb(mag, cmin, cmax):
    """
    Return a tuple of floats between 0 and 1 for the red, green and
    blue amplitudes.
    """
    mag  = float(mag)
    cmin = float(cmin)
    cmax = float(cmax)
    try:
        # normalize to [0,1]
        x = float(mag-cmin)/float(cmax-cmin)
    except:
        # cmax = cmin
        x = 0.5
    blue = min((max((4*(0.75-x), 0.)), 1.))
    red  = min((max((4*(x-0.25), 0.)), 1.))
    green= min((max((4*math.fabs(x-0.5)-1., 0.)), 1.))
    return (red, green, blue)

def strRgb(mag, cmin, cmax):
    """
    Return a tuple of strings to be used in Tk plots.
    """

    red, green, blue = floatRgb(mag, cmin, cmax)
    return "#%02x%02x%02x" % (red*255, green*255, blue*255)

def rgb(mag, cmin, cmax):
    """
    Return a tuple of integers to be used in AWT/Java plots.
    """

    red, green, blue = floatRgb(mag, cmin, cmax)
    return (int(red*255), int(green*255), int(blue*255))

def htmlRgb(mag, cmin, cmax):
    """
    Return a tuple of strings to be used in HTML documents.
    """
    return "#%02x%02x%02x"%rgb(mag, cmin, cmax)


def removeNulls(serie):
    """Check y values for None and kick them out if they are."""
    result = []
    for point in serie:
        if point[1] == None:
            nTdebug("Kicking point with None y at x: %s", point[0] )
            continue
        result.append( point )
    return result

def integerNumberOnly(x,_dummy):
    'Returns empty string wherever not integer x'
    remainder = math.fabs(x) % 1.0
    if remainder > 0.001:
        return ''
    return '%.0f' % x

def cmapWithAlpha(z,palette,minAlpha=.5, maxAlpha=1., underAlpha=0., overAlpha=1.):
    """Scales the alpha from the given min to max value based on input from 0 to 1."""

    diffAlpha = maxAlpha - minAlpha
    tmp = palette(z)
    for i in xrange(z.shape[0]):
        for j in xrange(z.shape[1]):
            # Generate the transparency (alpha mixing)
            v = z[i,j]
            if v < 0.:
                alpha = underAlpha
            elif v > 1.:
                alpha = overAlpha
            else:
                alpha = minAlpha + v * diffAlpha
            tmp[i,j][3] = alpha
#            nTdebug('v: %5.2f alpha %5.2f' % (v,alpha))
    return tmp

def ssTypeToIdx(ssType):
    """Note that this is not the same as mapDssp2Int in reqDssp.py
    This one's keyed to the colormaps which are alphabetically.
    """
    typeMap = {' ': 0, 'H': 1, 'S': 2}
    idx = getDeepByKeysOrAttributes(typeMap, ssType)
    return idx

def ssIdxToType(idxType):
    """Note that this is not the same as mapDssp2Int in reqDssp.py
    This one's keyed to the colormaps.
    """
    typeMapRev = {0: ' ',1: 'H',2: 'S'} # could have used an array.
    ssType = getDeepByKeysOrAttributes(typeMapRev, idxType)
    return ssType
