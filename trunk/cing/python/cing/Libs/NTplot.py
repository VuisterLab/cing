from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NThistogram
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTsort
from cing.Libs.NTutils import isAlmostEqual
from cing.Libs.NTutils import limitToRange
from cing.Libs.matplotlibExt import blue_inv
from cing.Libs.matplotlibExt import green_inv
from cing.Libs.matplotlibExt import yellow_inv
from cing.PluginCode.required.reqDssp import DSSP_STR
from cing.PluginCode.required.reqDssp import getDsspSecStructConsensus
from cing.PluginCode.required.reqDssp import to3StateUpper
from cing.PluginCode.required.reqProcheck import CONSENSUS_SEC_STRUCT_FRACTION
from cing.PluginCode.required.reqProcheck import SECSTRUCT_STR
from cing.PluginCode.required.reqWhatif import INOCHK_STR
from cing.PluginCode.required.reqWhatif import VALUE_LIST_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.core.constants import SCALE_BY_MAX
from cing.core.constants import SCALE_BY_SUM
from cing.core.parameters import plotParameters
from colorsys import hsv_to_rgb
from copy import deepcopy
from matplotlib import pyplot
from matplotlib.patches import Ellipse
from matplotlib.patches import Patch
from matplotlib.path import Path
from matplotlib.pylab import * #@UnusedWildImport for such functions as amax, arange, multiply, mat, etc...

try:
    import Image
    haveImage = True
#    NTdebug("Installed python Image library (pil)")
except ImportError:
    NTerror("Failed to import python Image library (pil); certain plot options will fail")
    haveImage = False
#end try

dpi=72.27 # Latex definition
inches_per_pt = 1./dpi
golden_mean = (math.sqrt(5.)-1.)/2.     # Aesthetic ratio where possible.
DEFAULT_FONT_SIZE = 12

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Plotting attributes
#-----------------------------------------------------------------------------


def NTplotAttributes( **kwds ):
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
    return NTplotAttributes( lineType=type, lineWidth=width, lineColor=color, alpha=alpha )
#end def

def boxAttributes( fill=True, fillColor='black', line=False, lineColor='black', alpha=1. ):
    return NTplotAttributes( lineType='solid', lineColor=lineColor, line=line,
                             fill=fill, fillColor=fillColor, alpha=alpha
                           )
#end def

def fontAttributes( font='Helvetica', size=DEFAULT_FONT_SIZE, color='black', alpha=1. ):
    return NTplotAttributes( font=font, fontSize=size, fontColor=color, alpha=alpha )
#end def

def fontVerticalAttributes( horizontalalignment='left', verticalalignment  = 'center', rotation   = 'vertical', size=DEFAULT_FONT_SIZE ):
    result = fontAttributes(size=size)
    result.horizontalalignment=horizontalalignment
    result.verticalalignment=verticalalignment
    result.rotation=rotation
    return result

def pointAttributes( type='circle', size=4.0, pointEdgeWidth=2.0, color='black', alpha=1. ):
    return NTplotAttributes( pointType=type, pointSize=size, pointEdgeWidth=pointEdgeWidth, pointColor=color, alpha=alpha )
#end def

# Some default attributes
defaultAttributes  = NTplotAttributes()

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

# pylab
#            -     : solid line
#            --    : dashed line
#            -.    : dash-dot line
#            :     : dotted line
#            .     : points
#            ,     : pixels
#            o     : circle symbols
#            ^     : triangle up symbols
#            v     : triangle down symbols
#            <     : triangle left symbols
#            >     : triangle right symbols
#            s     : square symbols
#            +     : plus symbols
#            x     : cross symbols
#            D     : diamond symbols
#            d     : thin diamond symbols
#            1     : tripod down symbols
#            2     : tripod up symbols
#            3     : tripod left symbols
#            4     : tripod right symbols
#            h     : hexagon symbols
#            H     : rotated hexagon symbols
#            p     : pentagon symbols
#            |     : vertical line symbols
#            _     : horizontal line symbols
#            steps : use gnuplot style 'steps' # kwarg only

mappingPointType2MatLibPlot = {
    'none':             'None',
    'plus':             '+',
    'circle':           'o',
    'square':           's',
    'filled circle':    'o',
    'triangle':         '^',
     }
"""          linestyle or ls: [ '-' | '--' | '-.' | ':' | 'steps' | 'None' | ' ' | '' ] """


mappingLineType2MatLibPlot = {
    SOLID_LINE_TYPE:        '-',
    DOTTED_LINE_TYPE:       ':',
    LONGDASHED_LINE_TYPE:   '--',
    DASHDOT_LINE_TYPE:      '-.',
    NONE_LINE_TYPE:         ' '
    }


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


class NTplot( NTdict ):
    """
    Base plotting class but don't forget to instantiate a NTplotSet first.
    """
    def __init__( self, **kwds ):
        NTdict.__init__( self )
        self.__CLASS__    = 'NTplot'
        self.font         = 'Helvetica'

        self.title        = None
        self.xLabel       = None
        self.yLabel       = None

        self.aspectRatio  = 1.0    # Aspect ratio
        self.xRange       = None   # x-axis (min,max) tuple, None is autoscale
        self.yRange       = None   # y-axis (min,max) tuple, None is autoscale

        self.xTicks       = None   # x-axis tics-list, None is autotics. Empty list is not ticks.
        self.yTicks       = None   # y-axis tics-list, None is autotics

        self.xAxis        = True
        self.yAxis        = True

        self.xGrid        = True   # x-axis grid toggle
        self.yGrid        = True   # y-axis grid toggle

        self.plotID       = "Plot A" # will be overridden by NTplotSet where needed.
                                        # Can be numeric e.g. in case of rectangular layout of set.
        self.axis = axes([.1, .1, .8, .8 ] ) # To be overridden by NTplotSet if needed. # ll_x, ll_y, w, h

        self.update( kwds )

    def convert_yunits(self, yValueList):
        """ Convert from [0,1] to self.yRange"""
        yViewInterval = self.yRange
        bottom = yViewInterval[0]
        top    = yViewInterval[1]
        height = top-bottom

        result = []
        for v in yValueList:
            r = bottom + height * v
            result.append( r )
#            NTdebug('NTplot.scaleAndMove_yValuesFromAxesToData: %8.3f becomes: %8.3f with bottom,top %8.3f,%8.3f' % (v,r,bottom,top) )
        return result

    def move( self, point ):
        self.currentPoint = point

    def draw( self, endPoint, attributes=defaultAttributes ):
        if not attributes:
            attributes=defaultAttributes
        xdata=(self.currentPoint[0], endPoint[0])
        ydata=(self.currentPoint[1], endPoint[1])
#        NTdebug("xdata: " + `xdata`)
#        NTdebug("ydata: " + `ydata`)
        line2D = Line2D(xdata, ydata)
        attributesMatLibPlot = self.mapAttributes2MatLibPlotLine2D(attributes)
        line2D.set( **attributesMatLibPlot )
        self.axis.add_artist(line2D)
        self.currentPoint = endPoint
    #end def

    def line( self, startPoint, endPoint, attributes=defaultAttributes):
        if not attributes:
            attributes=defaultAttributes
        self.move( startPoint )
        self.draw( endPoint=endPoint, attributes=attributes )
    #end def

    def lines( self, points, attributes=None ):
        if not attributes:
            attributes=defaultAttributes
        if len(points) == 0:
            return
        self.move( points[0] )
        for p in points[1:]:
            self.draw( endPoint=p, attributes=attributes )

    def scatter(self, x,y,s=20, c='b',marker=None,verts =None):
        """Return true on error UNTESTED.

        Make a scatter plot of x versus y, where x, y are 1-D sequences
        of the same length, N.

        s is a size in points^2.  It is a scalar
          or an array of the same length as x and y.

        c is a color and can be a single color format string,

        If marker is None and verts is not None, verts is a sequence
        of (x,y) vertices for a custom scatter symbol.

        s is a size argument in points squared.
        """
        self.axis.scatter(x,y,s,c,marker=marker,verts =verts)

    def ellipse(self, point, width=3.0, height=1.0, color=None, alpha=None):
        """Return true on error UNTESTED."""
        # Expose matplot lib routine.
#        e = Ellipse(startPoint=point, width=0.2*rand(), height=0.2*rand())
        e = Ellipse(xy=point, width=width, height=height)
        e.set_clip_box(self.axis.bbox)
        if color:
            e.set_facecolor(color)
            e.set_edgecolor(color)
        if alpha:
            e.set_alpha(alpha)
        self.axis.add_artist(e)

    def drawVerticalLines( self, xlocList ):
        if self.yRange == None:
            self.autoScaleY(None) # sets the yRange needed below.

        for xloc in xlocList:
            pointList = []
            pointList.append( (xloc, self.yRange[0]) )
            pointList.append( (xloc, self.yRange[1]) )
#            pointList = self.convert_yunits(pointList)
            self.lines( pointList )

    def box( self, point, sizes, attributes=None ):
#        NTdebug("box with point, sizes: %s %s" %( point, sizes))
        if not attributes:
            attributes=defaultAttributes

        attributesMatLibPlot = self.mapAttributes2MatLibPatches(attributes)
#        NTdebug("Using attributesMatLibPlot: %s" % attributesMatLibPlot)
        rectangle = Rectangle(point,
            width=sizes[0],
            height=sizes[1],
            **attributesMatLibPlot )
        self.axis.add_artist(rectangle)
#            NTdebug("box added to artist")
    #end def

    def mapAttributes2MatLibPlotLine2D(self, attributes=defaultAttributes):
        if not attributes:
            attributes=defaultAttributes
        result = {}
        result['color']  = None
        result['marker'] = 'None'


#            'linewidth'      : None, # all Nones default to rc
#            'linestyle'      : None,
#            'color'          : None,
#            'marker'         : None,
#            'markersize'     : None,
#            'markeredgewidth': None,
#            'markeredgecolor': None,
#            'markerfacecolor': None,
#            'antialiased'    : None,
#            'dash_capstyle'  : None,
#            'solid_capstyle' : None,
#            'dash_joinstyle' : None,
#            'solid_joinstyle': None,
#        }
        keys = attributes.keys()
        # input:
#        ['fill', 'fillColor', 'font', 'fontColor', 'fontSize', 'line', 'lineColor', 'lineType', 'lineWidth',
#         'pointColor', 'pointSize', 'pointType', 'textAlign']

#        NTdebug("attributes: " + attributes.format())
        if 'pointType' in keys:
            if attributes.pointType:
                if mappingPointType2MatLibPlot.has_key(attributes.pointType):
#                    print "doing pointType"
                    result['marker'] =  mappingPointType2MatLibPlot[attributes.pointType]
                else:
                    NTcodeerror("Failed to map point type ["+`attributes.pointType`+"]to mat lib plot's marker id)")
                    return True
        if 'pointColor' in keys:
#            print "doing pointColor"
            result['markeredgecolor'] =  attributes.pointColor
            result['markerfacecolor'] =  attributes.pointColor
            result['color']           =  attributes.pointColor
        if 'pointSize' in keys:
#            print "doing pointSize"
            result['markersize'] =  attributes.pointSize
        if 'pointEdgeWidth' in keys:
#            print "doing pointEdgeWidth"
            result['markeredgewidth'] =  attributes.pointEdgeWidth

        if 'lineColor' in keys:
#            print "doing lineColor"
            result['color']           =  attributes.lineColor
        if 'lineType' in keys:
#            print "doing lineType (linestyle)"
            if not mappingLineType2MatLibPlot.has_key( attributes.lineType ):
                NTcodeerror("Failed to set line style [%s] because it is absent in mappingLineType2MatLibPlot %s" %
                            (attributes.lineType, mappingLineType2MatLibPlot))
            else:
                result['linestyle']       =  mappingLineType2MatLibPlot[attributes.lineType]
        if 'color' in keys:
#            print "doing color"
            result['color']           =  attributes.color
        if 'fill' in keys:
            if attributes.fill: # it might still be set to False.
    #            print "doing fill"
                markerColor = result['color']
                if 'pointColor' in keys:
                    markerColor = attributes.pointColor
                elif 'lineColor' in keys:
                    markerColor = attributes.lineColor
                result['markeredgecolor'] =  markerColor
                result['markerfacecolor'] =  markerColor
            else:
                # AWSS: for matplotlib 0.91.3 , None is not acceptable anymore.
                result['markerfacecolor'] =  'none' #None # it might have been set above.
                #attributes.alpha = 0.0
#    a.pointType  = None   # in matplotlib: marker
#    a.pointSize  = 2.0    # in matplotlib: markersize
#    a.pointColor = 'blue' # in matplotlib: markeredgecolor

        if 'alpha' in keys:
#            print "doing alpha"
            result['alpha']           =  attributes.alpha
#        NTdebug("result[attributes: " + `result[)
        return result

    def mapAttributes2MatLibPatches(self, attributes=defaultAttributes):
        if not attributes:
            attributes=defaultAttributes
        result = {}
        # Patch attributes.
#                 edgecolor=None,
#                 facecolor=None,
#                 linewidth=None,
#                 antialiased = None,
#                 hatch = None,
#                 fill=1,
        # Input
#                facecolor=attributes.fillColor,
#                edgecolor=attributes.lineColor,
#                fill=attributes.fill,

        keys = attributes.keys()
        if 'alpha' in keys:
            result['alpha']               =  attributes.alpha
        if 'fill' in keys:
            result['fill']                =  attributes.fill
        if 'fillColor' in keys:
            result['facecolor']           =  attributes.fillColor # is facecolor used if fill is False?
        if 'lineColor' in keys:
            result['edgecolor']           =  attributes.lineColor
#        NTdebug("input  mapAttributes2MatLibPatches: " + `attributes`)
#        NTdebug("result mapAttributes2MatLibPatches: " + `result`)
        return result

    def mapAttributes2MatLibText(self, attributes=defaultAttributes):
        # Creates dictionary as expected for Text attributes
        if not attributes:
            attributes=defaultAttributes
        result = {}
        keys = attributes.keys()
        if 'fontColor' in keys:
            result['color']                =  attributes.fontColor
        if 'rotation' in keys:
            result['rotation']             =  attributes.rotation
        if 'horizontalalignment' in keys:
            result['horizontalalignment']            =  attributes.horizontalalignment
        if 'verticalalignment' in keys:
            result['verticalalignment']            =  attributes.verticalalignment
        return result


    def removeMarkerAttributes( self, attributesMatLibPlot):
        del(attributesMatLibPlot['marker'])
        del(attributesMatLibPlot['markeredgecolor'])
        del(attributesMatLibPlot['markerfacecolor'])

    def setMatLibPlotLine2DListPropsPoint( self, line2DList, attributesMatLibPlot):
        for line2D in line2DList:
            line2D.set( **attributesMatLibPlot )

    def point( self, point, attributes=defaultAttributes ):
        """ Add a point
            add xErrorBar if len(points)>2
            add yErrorBar if len(points)>3       """

        if not attributes:
            attributes=defaultAttributes
        if attributes.has_key('pointType'):
            if not attributes.pointType:
                attributes.pointType= 'none' # Changed to have no point as this is more common for all.
        attributesMatLibPlot = self.mapAttributes2MatLibPlotLine2D(attributes)
#            print attributesMatLibPlot['marker']
        x = point[0]
        y = point[1]
        axes(self.axis) # Claim current axis.
        line2D, = plot( [x], [y] )
#            NTdebug('before getp(line2D):')
#            getp(line2D)
        line2D.set( **attributesMatLibPlot)
        xerror=None
        yerror=None
        if len(point) >2:
            xerror=point[2]
            if len(point) >3:
                yerror=point[3]
#            (l0, caplines, barcols) = errorbar([x], [y], xerr=xerror, yerr=yerror, ecolor=attributesMatLibPlot['color'])
        errorbar([x], [y], xerr=xerror, yerr=yerror, ecolor=attributesMatLibPlot['color'])
#            line2Dlist = NTlist() # Allow appending of lists.
#            line2Dlist.append(l0)
#            line2Dlist.addList(caplines)
#            line2Dlist.addList(barcols)
#            attributesMatLibPlotNoMarker = self.removeMarkerAttributes(attributesMatLibPlot)
#            self.setMatLibPlotLine2DListPropsPoint( line2Dlist, attributesMatLibPlotNoMarker)
    #end def

    def points( self, points, attributes=defaultAttributes ):
        if not attributes:
            attributes=defaultAttributes
        if len(points) == 0:
            return
        for p in points:
            self.point( p, attributes )
        #end for
    #end def

    def labelAxes(self, point, text, attributes=defaultAttributes ):
        """Point needs to be specified in axis coordinate system [0,1]
        """
        kwds = self.mapAttributes2MatLibText(attributes)
#            NTdebug("In labelAxes using kwds: %s", kwds)
        self.axis.text( point[0], point[1], text,
            transform=self.axis.transAxes, **kwds)

    def label( self, point, txt, attributes=defaultAttributes ):
        """Point needs to be specified in data coordinate system
        """
        if not attributes:
            attributes=defaultAttributes
        kwds = self.mapAttributes2MatLibText(attributes)
#        NTdebug("Found kwds: %s" % kwds)
        startPoint=(point[0], point[1])
        axes(self.axis) # Claim current axis.
        pyplot.text(startPoint[0],startPoint[1],txt, **kwds)
    #end def

    def labeledPoint( self, point, text, attributes=defaultAttributes ):
        if not attributes:
            attributes=defaultAttributes
        self.point( point, attributes )
        self.label( point, text, attributes )
    #end def

    def setYrange(self, range):
        self.yRange = range
        ylocator = self.axis.yaxis.get_major_locator()
        ylocator.set_bounds( range[0], range[1] )

    def autoScaleYByValueList( self, valueList, startAtZero=False, useIntegerTickLabels=False ):
        pointList = []
        for i in range(len(valueList)):
            item = (None,valueList[i])
            pointList.append(item)
        return self.autoScaleY( pointList, startAtZero )

    def autoScaleX( self, pointList, startAtZero=False, useIntegerTickLabels=False ):
        """Using the list of points autoscale the y axis.
        If no list is given then the routine simply returns now.
        If the list only contains nulls the min and max will be assumed 0 and 1.
        If the min equals the max then the max is simply taken as min increased by one.
        If the min is None then the min is assumed to be zero and max will become one.
        This guarantees a y range.
        """
        min = None
        max = None
        if not pointList:
            return

        for point in pointList:
            v = point[1]
            if v == None:
                continue
            if min == None:
                min = v
                max = v
                continue
            if  v < min:
                min = v
            if  v > max:
                max = v

        if min == None or max == None:
#            NTdebug('Only None values in autoScaleY pointList found')
            min = 0.0
            max = 1.0

        if min == max: # Zero range is impossible.
            if min == None:
                min = 0.
            max = min + 1.

        if startAtZero and min >= 0.:
            min = 0.

#        NTdebug('autoScaleY to min,max: %8.3f %8.3f' % (min,max) )
        xlocator = self.axis.xaxis.get_major_locator()
        xlocator.set_bounds( min, max )
        self.axis.autoscale_view( scalex=True, scaley=False)
        self.xRange = self.axis.get_xlim()
        if useIntegerTickLabels:
            formatter = FuncFormatter(integerNumberOnly)
            xaxis = self.axis.xaxis
            xaxis.set_major_formatter( formatter )


    def autoScaleY( self, pointList, startAtZero=False, useIntegerTickLabels=False, useVerboseLocator=False ):
        """Using the list of points autoscale the y axis.
        If no list is given then the routine simply returns False.
        If the list only contains nulls the min and max will be assumed 0 and 1.
        If the min equals the max then the max is simply taken as min increased by one.
        If the min is None then the min is assumed to be zero and max will become one.
        This guarantees a y range.
        """

#        NTdebug( 'autoScaleY for list: %s' % (pointList) )

        min = None
        max = None
        if len(pointList) == 0:
            return

        for point in pointList:
            v = point[1]
            if v == None:
                continue
            if min == None:
                min = v
                max = v
                continue
            if  v < min:
                min = v
            if  v > max:
                max = v

        if min == None or max == None:
#            NTdebug('Only None values in autoScaleY pointList found')
            min = 0.0
            max = 1.0

        if min == max: # Zero range is impossible.
            if min == None:
                min = 0.
            max = min + 1.

        if startAtZero and min >= 0.:
            min = 0.

        NTdebug('autoScaleY to min,max: %8.3f %8.3f' % (min,max) )
        if not useVerboseLocator:
            ylocator = self.axis.yaxis.get_major_locator()
        else:
            NTerror("This part of the code needs to be tested")
#            ylocator = MaxNLocator(nbins=20) # instead of default 10
            ylocator = MultipleLocator(base=0.05) # instead of default 10

            self.axis.yaxis.set_major_locator(ylocator)
        ylocator.set_bounds( min, max )

        NTdebug('get_autoscaley_on: %s' % self.axis.get_autoscaley_on())
        self.axis.autoscale_view( scalex=False, scaley=True)
        self.yRange = self.axis.get_ylim()
        NTdebug('yRange set by matplotlib to min,max: ' + `self.yRange` )
        if useIntegerTickLabels:
            formatter = FuncFormatter(integerNumberOnly)
            yaxis = self.axis.yaxis
            yaxis.set_major_formatter( formatter )


    def updateSettings( self ):
#        NTdebug("Now in updateSettings")

        if not self.axis:
            raise "No axis object in NTplot"
        if not isinstance(self.axis, Axes):
            raise "Axis in NTplot not of correct type."
        axes(self.axis) # Claim current axis.
        if self.title:
            title( self.title )
        if self.xLabel:
            xlabel(self.xLabel)
        if self.yLabel:
            ylabel(self.yLabel)

        if isinstance(self.xTicks, list):
            if isinstance(self.xTicks[0],str):
                xticks(arange(0.5,len(self.xTicks)+0.5),self.xTicks)
            else:
                xticks(self.xTicks)# A list with actual values like 0,60,120...
            # or empty
        if isinstance(self.yTicks, list):
            if isinstance(self.yTicks[0],str):
                yticks(arange(0.5,len(self.yTicks)+0.5),self.yTicks)
            else:
                yticks(self.yTicks)# A list with actual values like 0,60,120...

        if self.xRange is not None:
            xlim(self.xRange)
#                NTdebug("Set the xlim in MatPlotLib to: %s %s" % (self.xRange))
        if self.yRange is not None:
            ylim(self.yRange)
#                NTmessage("Set the ylim in MatPlotLib")
        if self.xGrid is not None:
            grid(True)
        else:
            grid(False)
    # end def

    def histogram( self, theList, low, high, bins, leftMargin=0.05, rightMargin=0.05,
                   attributes=defaultAttributes, valueIndexPairList=None ):
        if not attributes:
            attributes=defaultAttributes
#        NTdebug("Creating number of bins: " + `bins`)
#        NTdebug("theList: " + `theList`)
        if not theList:
#            NTdebug("empty input not adding histogram")
            return # Nothing to add.
        his = NThistogram( theList, low, high, bins ) # A NTlist
        self.maxY = max(his)

        step = (high-low)/bins
        ind = arange(low,high,step)  # the x locations for the groups
#            NTdebug("Creating x coor for bins: " + `ind`)
        axes(self.axis) # Claim current axis.
        _patches = bar(ind, his, step,
            color    =attributes.fillColor,
            edgecolor=attributes.fillColor)

        if valueIndexPairList: # Were dealing with outliers.
#                NTdebug("Annotating the outliers with a arrow and string")
            tmpValueIndexPairList = deepcopy(valueIndexPairList)
            tmpValueIndexPairList = NTsort(tmpValueIndexPairList, 1)

            xlim = self.axis.get_xlim()
            ylim = self.axis.get_ylim()
            _ylim_min, ylim_max = ylim
#                NTdebug("xlim: " + `xlim`)
#                NTdebug("ylim: " + `ylim`)
            outlierLocHeight = ylim_max # In data coordinate system
            outlierLocHeightMin = ylim_max*.1 # In data coordinate system
#                NTdebug("tmpValueIndexPairList: " + `tmpValueIndexPairList`)
            for item in tmpValueIndexPairList:
                value = item[1]
                modelNum = item[0]
                if not value: # Don't annotate zero values.
                    continue
                outlierLocHeight -= 0.1*ylim_max # Cascade from top left to bottom right.
                if outlierLocHeight < outlierLocHeightMin:
                    outlierLocHeight = outlierLocHeightMin
#                    NTdebug("Setting data point to: " + `value` +", 1")
#                    NTdebug("Setting text point to: " + `value` +", "+ `outlierLocHeight`)
                self.axis.plot([value], [1], 'o',color=attributes.fillColor,markeredgecolor=attributes.fillColor,markersize=3)
                self.axis.annotate("model "+`modelNum`,
#                                startPoint=(0.05, 1),                       # in data coordinate system; assuming only one occurrence.
                            xy=(value+0.01, 1),                       # in data coordinate system; assuming only one occurrence.
                            xytext=(value, outlierLocHeight),
                            xycoords='data', # default: use the axes data coordinate system
                            textcoords='data',
                            arrowprops=dict(facecolor=attributes.fillColor,
                                            edgecolor=attributes.fillColor,
                                            shrink=0.05,
                                            width=1, # Width of arrow
                                            headwidth=4
                                            ),
                            horizontalalignment='left',
                            verticalalignment='bottom',
                            )
            # Do at the end because the plot command resets the boundaries?
            self.axis.set_ylim(ymax = ylim_max+1) # get some clearance at the top

    def barChart( self, barList, leftMargin=-0.5, rightMargin=0.5, attributes=defaultAttributes ):
        """
        Plot a bars at x-leftMargin to x+rightMargin, y height

        barList: list of (x, y) tuples
        """
        if not attributes:
            attributes=defaultAttributes

        for x,y in barList:
            self.box( point = ( x+leftMargin, 0.0 ),
                      sizes = ( rightMargin-leftMargin, float(y) ),
                      attributes = attributes)

    def get_ylim(self):
        return self.axis.get_ylim()

    def get_ticklines(self):
        'Return the ticklines lines as a list of Line2D instance; overcoming a lack of "feature" in api'
#        print ax
        lines = []
        xaxis = self.axis.get_xaxis()
        yaxis = self.axis.get_yaxis()
        for axis in [ xaxis, yaxis ]:
            for tick in axis.majorTicks:
                lines.append(tick.tick1line)
                lines.append(tick.tick2line)
            for tick in axis.minorTicks:
                lines.append(tick.tick1line)
                lines.append(tick.tick2line)
        return silent_list('Line2D ticklines', lines)

    def setTickLineWidth(self, size=1):
        tlList = self.get_ticklines()
        for tl in tlList:
            tl.set_markeredgewidth(size) # Unreported feature.

    def setMinorTicks(self, space):
        minorLocator = MultipleLocator(space)
        self.axis.xaxis.set_minor_locator(minorLocator)
        minorLocator = MultipleLocator(space)
        self.axis.yaxis.set_minor_locator(minorLocator)
        self.setTickLineWidth()


    def imshow(self, imageFileName):
        alpha = 0.05 # much lower than any background.
        im = Image.open( imageFileName )
#        s = im.tostring()
#        rgb = fromstring( s, UInt8).astype(Float)/255.0
#        rgb = resize(im, (im.size[1],im.size[0], 3))

        extent = self.xRange + self.yRange
        _image = imshow(im,
                        alpha=alpha,
                        extent=extent,
                        origin='lower')

    def dihedralComboPlot(self, histList, minPercentage =  2.0, maxPercentage = 20.0, scaleBy = SCALE_BY_MAX ):
        """Image histogram as in Ramachandran plot for coil, helix, sheet.

        Return True on error.

        Input histogram should be the bare counts using floats.
        This routine used to calculate the c_dbav, s_dbav but no more.

        scaleBy can be Max, or Sum
        """

        alpha = 0.8 # was 0.8; looks awful with alpha = 1
        extent = self.xRange + self.yRange
        # make sure helix and sheet are plotted over coil

        # When matplotlib 0.99.1.1 is the default this can obsolete matplotlibExt.py in CING.
#        blue_inv   = colors.LinearSegmentedColormap.from_list('inv_blue', ('white', 'blue'))
#        green_inv  = colors.LinearSegmentedColormap.from_list('inv_green', ('white', 'green'))
#        yellow_inv = colors.LinearSegmentedColormap.from_list('inv_yellow', ('white', 'yellow'))

        cmapList= [   green_inv, blue_inv, yellow_inv ]
        colorList= [ 'green',   'blue',   'yellow']
#        i = 0
        i = 0
        if len(histList) > len(cmapList):
            NTerror("Found length of histList:%d larger than cmapList's:%d" % ( len(histList),len(cmapList)))
            return True
        for i,myHist in enumerate(histList):
#        for myHist in [ histList[i] ]:
#            NTmessage('myHist: %s' % myHist)
#            print myHist
            if myHist.dtype != 'float64':
                NTerror("expected a histogram matrix with float values but found type: %s" % myHist.dtype)
                return True
            if scaleBy == SCALE_BY_MAX:
                maxHist = amax( myHist, axis = None ) # axis parameter should be None by default; just checking if I use the right api.
#                minHist = amin( myHist )
#                NTdebug("maxHist: %s" % maxHist)
#                NTdebug("minHist: %s" % minHist)
                factor = 100./maxHist
                myHist *= factor
            elif scaleBy == SCALE_BY_SUM:
                sumHist = sum( myHist, axis = None ) # axis parameter should be None by default; just checking if I use the right api.
#                NTdebug("sumHist: %s" % sumHist)
                factor = 100./sumHist
                myHist *= factor
            else:
                NTerror("parameter invalid in dihedralComboPlot")
                return True
            # Just make a copy...
            myHist = ma.masked_where(myHist <= minPercentage, myHist, copy=1)
            # JFD: there might be a bug in my code or in matplotlib that prevents me from using the under
            # the above is a workaround in order to use the 'bad' utility of the api.
            # The problem is that it doesn't do nice alpha mixing so disabled again to find solution.
#            NTmessage('myHist (scaled/masked): %s' % myHist)

            if True:
                palette = cmapList[i]
                palette.set_under(color = 'w', alpha = 0.0 ) # alpha is 0.0
                palette.set_over( color = colorList[i], alpha = 1.0) # alpha is 1.0 Important to make it a hard alpha; last plotted will rule.
                palette.set_bad(color = 'w', alpha = 0.0 )
#            else:
#                # Set up a colormap for debugging
#                palette = cm.gray # failed for JFD after switching to Eclipse 35. Probably not related.
#                palette.set_over('r', 1.0)
#                palette.set_under('g', 1.0)
#                palette.set_bad('b', 1.0)
                # Alternatively, we could use
                # palette.set_bad(alpha = 0.0)
                # to make the bad region transparent.  This is the default.
                # If you comment out all the palette.set* lines, you will see
                # all the defaults; under and over will be colored with the
                # first and last colors in the palette, respectively.

#            palette._set_extremes()

            norm = Normalize(vmin = minPercentage,
                                    vmax = maxPercentage, clip = True) # clip is False
#            NTdebug("under: %s" % str(palette._rgba_under))
#            NTdebug("over : %s" % str(palette._rgba_over))
#            NTdebug("bad  : %s" % str(palette._rgba_bad))

            imshow( myHist,
                    interpolation='bicubic',
#                    interpolation = 'nearest', # bare data.
                    origin='lower',
                    extent=extent,
                    alpha=alpha,
                    cmap=palette,
                    norm = norm
                     )
#            NTdebug('plotted %d %s' % (i, cmapList[i].name))
        # end for

    def plotDihedralRestraintRanges2D(self, lower1, upper1,lower2, upper2, fill=True, fillColor=None):

        alpha = 0.3
        SMALL_ANGLE_DIFF_FOR_PLOT = 0.1

        plotparamsXmin, plotparamsXmax = (self.xRange)
        plotparamsYmin, plotparamsYmax = (self.yRange)

        plotparams = plotParameters.getdefault("None",'dihedralDefault')
        if fill and not fillColor:
            fillColor = plotparams.lower

        bounds1 = NTlist(lower1, upper1)
        bounds2 = NTlist(lower2, upper2)
        bounds1.limit(plotparamsXmin, plotparamsXmax)
        bounds2.limit(plotparamsYmin, plotparamsYmax)

        # When the bounds are almost the same then make the range a very thinny one instead of full circle.
        if isAlmostEqual( bounds1, SMALL_ANGLE_DIFF_FOR_PLOT ):
            bounds1[1] = bounds1[0] + SMALL_ANGLE_DIFF_FOR_PLOT
        if isAlmostEqual( bounds2, SMALL_ANGLE_DIFF_FOR_PLOT ):
            bounds2[1] = bounds2[0] + SMALL_ANGLE_DIFF_FOR_PLOT
#        NTdebug("bounds1 : %s" % bounds1)
#        NTdebug("bounds2 : %s" % bounds2)

        boxAttr = boxAttributes(fill=fill, fillColor=fillColor, alpha=alpha)
#        NTdebug("boxAttr : %s" % boxAttr)

        if bounds1[0] < bounds1[1]: # one or two boxes
            if bounds2[0] < bounds2[1]: # single box thank you
                point = (bounds1[0], bounds2[0]) # lower left corner of only box.
                sizes = (bounds1[1]-bounds1[0],bounds2[1]-bounds2[0])
                self.box(point, sizes, attributes=boxAttr )
            else: # split box vertically.
                # top box
                point = (bounds1[0], bounds2[0]) # lower left corner of first box.
                sizes = (bounds1[1]-bounds1[0],plotparamsYmax-bounds2[0])
                self.box(point, sizes, attributes=boxAttr)
                # bottom box
                point = (bounds1[0], plotparamsYmin) # lower left corner of second box.
                sizes = (bounds1[1]-bounds1[0], bounds2[1]-plotparamsYmin)
                self.box(point, sizes, attributes=boxAttr)
        else: # at least two or four boxes
            if bounds2[0] < bounds2[1]: # 2 boxes; left and right
                # left box
                point = (plotparamsXmin, bounds2[0]) # lower left corner of first box.
                sizes = (bounds1[1]-plotparamsXmin,bounds2[1]-bounds2[0])
                self.box(point, sizes, attributes=boxAttr)
                # right box
                point = (bounds1[0], bounds2[0]) # lower left corner of second box.
                sizes = (plotparamsXmax-bounds1[0], bounds2[1]-bounds2[0])
                self.box(point, sizes, attributes=boxAttr)
            else:  # 4 boxes; lower left ll, lr, upper left ul, ur.
                # ur
                point = (bounds1[0], bounds2[0])
                sizes = (plotparamsXmax-bounds1[0],plotparamsYmax-bounds2[0])
                self.box(point, sizes, attributes=boxAttr)
                # lr
                point = (bounds1[0], plotparamsYmin) # lower left corner of second box.
                sizes = (plotparamsXmax-bounds1[0], bounds2[1]-plotparamsYmin)
                self.box(point, sizes, attributes=boxAttr)
                # ul
                point = (plotparamsXmin, bounds2[0])
                sizes = (bounds1[1]-plotparamsXmin,plotparamsYmax-bounds2[0])
                self.box(point, sizes, attributes=boxAttr)
                # ll
                point = (plotparamsXmin, plotparamsYmin) # lower left corner of second box.
                sizes = (bounds1[1]-plotparamsXmin, bounds2[1]-plotparamsYmin)
                self.box(point, sizes, attributes=boxAttr)
            # end else
        # end else
    # end def
# end class

class NTplotSet( NTdict ):
    """Encapsulate one ore more plots in NTplotSet.
    NTplot can still be used by itself for creating and
    saving without reference to being a part of a NTplotSet.
    All info on where a NTplot is within a overall layout is
    maintained by NTplot instances themselves.
    This class attempts to insulate against specifics of the
    graphics library Matplotlib although currently no other
    lib has been implemented against.
    """
    def __init__( self, **kwds ):
        NTdict.__init__( self )
        self.close()
        self.__CLASS__    = 'NTplotSet'
        self.plotSet = {}
        """A collection within which data can be drawn
        """
        self.numRows = 1 # Don't have a meaning without a rectangular grid layout.
        self.numCols = 1 # Perhaps no need to maintain?
        self.hardcopySize = (400,400)
        self.update( kwds ) # Overwrites hardcopySize etc.
        self.graphicsOutputFormat = 'png'

#        NTdebug('Using self.hardcopySize: '+`self.hardcopySize`)=
    #end def

    def close( self ):
        "Closes a 'window'"
        close('all')
        cla() # clear current axes
        clf() # clear current figure

    def show( self ):
        self.updateSettings()
        show()

    def hardcopy( self, fileName, graphicsFormat = 'png' ):
        """        Returns True on error.         """

        self.updateSettings()
#        if not self.plotSet:
#            NTerror("no elements in NTplotSet")
#            return True

        fig_width_pt  = self.hardcopySize[0]
        if self.hardcopySize[1]:
            fig_height_pt = self.hardcopySize[1]
        else:
            fig_height_pt = int(fig_width_pt*golden_mean)
#            fig_size_pt   = [fig_width_pt,fig_height_pt]
#            print fig_size_pt
        fig_width     = fig_width_pt*inches_per_pt  # width in inches
        fig_height    = fig_height_pt*inches_per_pt # height in inches
        fig_size      = [fig_width,fig_height]

        params = {#'backend':          self.graphicsOutputFormat,
                  'figure.dpi':       dpi,
                  'figure.figsize':   fig_size,
                  'savefig.dpi':      dpi,
                  'savefig.figsize':  fig_size,
                   }
        rcParams.update(params)
        figure = gcf()
        figure.set_size_inches(  fig_size )
        savefig(fileName)

    def updateSettings( self ):

#            NTdebug("Getting hardcopySize: "+`self.hardcopySize`)
#            NTdebug("Setting sizeInches:   "+`fig_size`)


        for plotId in self.plotSet:
            p = self.plotSet[plotId]
            p.updateSettings()

    def getPlot(self, plotId):
        return self.plotSet[ plotId ]

    def addPlot(self, ntPlot, plotId="Plot from NTplotSet"):
        """Just add a plot that has been precreated"""
        self.plotSet[plotId] = ntPlot
        return self.getPlot(plotId)

    def createPlot(self, plotId="Plot from NTplotSet", *args):
        ntPlot = NTplot(plotId=plotId)
        self.plotSet[plotId] = ntPlot
        ntPlot.axis = Axes( *args )
        return self.getplot(plotId)

    def createSubplot(self, numRows, numCols, plotNum,
        useResPlot=False, molecule=None, resList=None ):
        """Layout an extra plot in a rectangular grid.
        e.g. 235 would return a
        fifth NTplot from
        -------------
        - 1 - 2 - 3 -
        - 4 - 5 - 6 -
        -------------
        """
        self.numRows = numRows
        self.numCols = numCols
        if useResPlot:
            ntPlot = ResPlot(plotID=plotNum,molecule=molecule,resList=resList) # use numeric value in case of rectangular grid.
        else:
            ntPlot = NTplot(plotID=plotNum) # use numeric value in case of rectangular grid.
        self.plotSet[plotNum] = ntPlot
        ntPlot.axis = subplot(numRows, numCols, plotNum)
        return self.getPlot(plotNum)

    def subplotsAdjust(self, **args ):
        subplots_adjust( **args )

class ResPlot(NTplot):
    """Plot class for sequence of residues
x coordinate is in 'data' coordinate system (sequence number)
y coordinate is in axis coordinates (from 0 to 1) when the renderer asks for the
    coordinate a conversion needs to take place."""

    SMALLEST_HELIX_LENGTH = 2
    MAX_WIDTH_IN_RESIDUES = 50 # Maximum number of residues in plot.

    colorHelixIn  = 'yellow'
    colorHelixOut = 'red'
    colorStrand   = 'cyan'
    colorCoil     = 'grey'
    colorBackbone = 'grey' # for nucleic acids
    colorBaseA    = 'yellow'
    colorBaseT    = 'red'
    colorBaseG    = 'green'
    colorBaseC    = 'purple'
    colorLine     = 'black'
    colorBackNoSecStruct = 'lightgrey'
#    resPerPlot    = 100 # Number of residues per plot"""

    hueRed  = 0.
    hueBlue = 0.68

    def __init__(self,**kwargs):
        """seq        Residue list for which to produce plots
        """
        NTplot.__init__(self, **kwargs)
#        self.molecule = None
#        self.resList = None # NTlist of residue objects.
        self.xRange = ( 0, ResPlot.MAX_WIDTH_IN_RESIDUES )
        self.xLabel = 'Sequence'
        self.resIconHeight =  1.
        self.iconBoxYheight= 0.16 # in axis coordinates [0,1] the height of the residue type icon.
        # was 0.18




    def getsecStructElementList(self):
        """Chop the molecule into segments of the same secondary structure type
        from consensus DSSP attribute.

        ' HHHHH   SSSS   ' becomes
        [ ' ', 'HHHH', '   ', 'SSSS', '   ' ] but then in residue objects.
        """

        result=[]
        secStructElement = []
        lastResNum = None
        lastChainName = None
        prevSecStruct = None

        for res in self.resList: # Exclude residues not in this plot's resList
            # detect a break
            isBroken = False
            if lastResNum == None:
                isBroken = True
            elif res.resNum != lastResNum + 1:
                isBroken = True
            elif res.chain.name != lastChainName:
                isBroken = True

            if isBroken:
                if secStructElement:
                    result.append(secStructElement)
                secStructElement=[]
                prevSecStruct = None

            lastResNum    = res.resNum
            lastChainName = res.chain.name

            l = res.getDeepByKeys(DSSP_STR,SECSTRUCT_STR)
#            NTdebug( 'getsecStructElementList l before reduced to 3 states: %s', l )
            secStruct = None
            if l:
                l = to3StateUpper( l )
                secStruct = l.getConsensus(CONSENSUS_SEC_STRUCT_FRACTION) # will set it if not present yet.

#            NTdebug('getsecStructElementList res: %s %s %s', res, l, secStruct)
            if  secStruct != prevSecStruct:
                if secStructElement:
                    result.append(secStructElement)
                secStructElement=[]
            secStructElement.append(res)
            prevSecStruct=secStruct

        if secStructElement:
            result.append(secStructElement)
#        NTdebug('getsecStructElementList result: %s', result)
        return result

    def setMinorTickerToRes(self):
#        minorFormatter = NullFormatter()
        self.axis.xaxis.set_minor_locator(MultipleLocatorByOffset(1)) # accept default offset of -.5 )
#        xaxis.set_minor_formatter( minorFormatter )

    def drawResTypes(self, ySpaceAxis=.06):
        """Since we want to color residue types and the current api of matplotlib
        is hard to extend that way we do this outside of it.
        """
#        seqLength = len(self.resList)

        iconBoxXstart = 0              # data
#        iconBoxXwidth = seqLength      # data
        iconBoxYstart = 1 + ySpaceAxis # axis
#        self.xRange       = (0,iconBoxXwidth)   # x-axis (min,max) tuple, None is autoscale

        i = 0
        for res in self.resList:
#            NTdebug("drawResTypes for: %s" % res )
            resChar = 'x'
            if res.shortName:
                resChar = res.shortName
            else:
                resChar = res.name

            if ( res.hasProperties('nucleic') and
                (resChar[0]=='r' or resChar[0]=='d') and
                len(resChar)>1):
                resChar = resChar[1:2] # truncate rc to c
            else:
                resChar = resChar[0:1] # truncate A171 to A

            resChar = resChar.upper()
            x = iconBoxXstart + i + 0.5
            y = self.convert_yunits([ iconBoxYstart ])[0] # convert to data coordinates
            text = resChar
            attributes = fontAttributes()
            attributes.fontColor=res.rogScore.colorLabel
            attributes.horizontalalignment='center'
#            NTdebug(`attributes`)
#            y = 5.0 # for testing
#            NTdebug("x,y: %s,%s" % (x,y))
            self.label( (x,y) , text, attributes )
            i += 1

    def drawResNumbers(self, showLabels=True):
        """If just the locators need to be set then disable the labels
        with the option set to False.
        Will also draw a vertical line to indicate the chain breaks.
        """
        majorFormatter = NullFormatter()
        if showLabels:
            majorFormatter = FormatResNumbersFormatter(self.resList)

        xaxis = self.axis.xaxis
        xaxis.set_major_formatter( majorFormatter )
        # Watch out next command also affects the minor tickers..
        xaxis.set_ticks_position('both')
        self.setMinorTickerToRes()
        self.axis.xaxis.set_major_locator (  LocatorResidueMajorTicks( self.resList ))
            #        xaxis.set_label_position('top')
#        xaxis.set_ticklabels('') # remove the major tick labels but keep the ticks.
#        tickList = xaxis.get_minor_ticks()
        locs = []
#        totalNumberResidues = len(self.resList)
        idx = -0.5
        lastResNum = None
        lastChainName = None
        for res in self.resList:
            # detect a break
            isBroken = False
            if lastResNum == None:
                isBroken = True
            elif res.resNum != lastResNum + 1:
                isBroken = True
            elif res.chain.name != lastChainName:
                isBroken = True
            lastResNum    = res.resNum
            lastChainName = res.chain.name
            idx += 1
            if isBroken:
                locs.append(idx)
        # skipping very first residue even if it's a break.
        if locs:
            locs = locs[1:]
        self.drawVerticalLines( locs )


    def drawResIcons(self, ySpaceAxis=.06):
        """Vary ySpaceAxis for raising it more depending on other items to be
        plotted
        Call AFTER scaling of axes. So all calls to matplotlib will be in 'data'
        coordinate system.
        JFD had y-axis coordinates in 'axes' coordindate system before. Now all variables not using data
        coordinate system are named with e.g. Axis as in ySpaceAxis.
        """
#        NTdebug("In drawResIcons ySpaceAxis is %s" % ySpaceAxis)
        kwargs = {'edgecolor':ResPlot.colorLine, 'facecolor':ResPlot.colorHelixIn, 'clip_on':None}


        iconBoxXstart = 0              # data coordinate system
        iconBoxYstartAxis = 1 + ySpaceAxis # axis coordinate system
        height = scale_yValuesFromAxesToData( self.axis, [self.iconBoxYheight])[0]
        iconBoxYstart = scaleAndMove_yValuesFromAxesToData(self.axis, [ iconBoxYstartAxis ])[0]

        # Get a background with Z-scores of accessibility.
        i = 0
        for res in self.resList:
            accessibilityZscoreList = res.getDeepByKeys(WHATIF_STR,INOCHK_STR,VALUE_LIST_STR)
            if not accessibilityZscoreList:
                accessibilityZscore = None
            else:
                accessibilityZscore = accessibilityZscoreList.average()[0]
            color = mapAccessibilityZscore2Color(accessibilityZscore) # get an rgb tuple
            startPoint = ( iconBoxXstart + i, iconBoxYstart)
#            NTdebug("RangeIcon: startPoint %s %s" % startPoint)
            p = RangeIcon( startPoint=startPoint,width=1,height=height, seq=1, axis=self.axis,edgecolor=color, facecolor=color, clip_on=None )
            self.axis.add_patch(p)
            i += 1

        # Get a icons for secondary structure
        secStructElementList = self.getsecStructElementList()
        i = 0
        for element in secStructElementList:
#                NTdebug(`element`)
            elementLength = len(element)
            res = element[0]
#                secStruct = getProcheckSecStructConsensus( res )
            secStruct = getDsspSecStructConsensus( res )
            if secStruct == 'H' and elementLength < 2: # Can't plot a helix of length 1 residue
                secStruct = None
            if secStruct == ' ':
                secStruct = None
#                NTdebug('res: %s, secStruct %s, and length: %d', res, secStruct, elementLength)

            width = elementLength
            startPoint = ( iconBoxXstart + i, iconBoxYstart)

            rangeIconList = RangeIconList( axis=self.axis,secStruct=secStruct,seq=elementLength,
                startPoint=startPoint,width=width,height=height,**kwargs)
            if rangeIconList.addPatches():
                NTerror("Failed to addPatches for element with residues: %s", element)
                continue
            for p in rangeIconList.patchList:
                self.axis.add_patch(p)
            i += elementLength
        # end for
    # end def
# end class

class RangeIconList:
    def __init__(self, axis=None, secStruct=' ', seq=1, startPoint=None, width=None, height=None, **kwargs):
        self.patchList= []
        self.seq      = seq
        self.secStruct= secStruct
        self.startPoint= startPoint
        self.width    = width
        self.height   = height
        self.axis     = axis
        self.kwargs   = kwargs
        if not self.axis:
            NTcodeerror('no self.axis in RangeIconList')
            return

    def addPatches(self):
        "Return True on error"
#        NTmessage("Doing addPatches for seq: %d", self.seq)

#        self.secStruct='H' #: disable after debugging.
        if self.secStruct=='S':
            p = StrandIcon(seq=self.seq, axis=self.axis, startPoint=self.startPoint,
                           width=self.width, height=self.height,**self.kwargs)
            if not p:
                NTerror("Failed to create StrandIcon")
                return True
            self.patchList.append( p )
        elif self.secStruct=='H':
            helixIconList = HelixIconList(seq=self.seq, startPoint=self.startPoint,
                width=self.width, height=self.height,axis=self.axis,**self.kwargs)
            if helixIconList.addPatches():
                NTerror("Failed to create HelixIconList")
                return True
            plist = helixIconList.patchList
            if not plist:
                NTerror("Failed to create any HelixIconList")
                return True
            for p in plist:
                self.patchList.append( p )
        elif self.secStruct==None:
#            p = CoilIcon(self.startPoint, self.width, self.height,self.seq, self.axis, **self.kwargs)
            kwargsLocal = {'edgecolor':ResPlot.colorLine, 'facecolor':ResPlot.colorCoil, 'clip_on':None}
            p = CoilIcon(seq=self.seq, axis=self.axis, startPoint=self.startPoint, width=self.width, height=self.height,**kwargsLocal)
            if not p:
                NTerror("Failed to create CoilIcon")
                return True
            self.patchList.append( p )
#        else:
#            NTerror("Failed to find one of 3 states, doing addPatches for seq: %d and self.secStruct: %s", (self.seq, self.secStruct))
#            return True

class HelixIconList(RangeIconList):
    """ Draw helices in half turn increments scale back x-coordinate to fit odd
        numbered residue helices.    """

#        HELIX_PERIOD = 4.- HELIX_HWIDTH # 3.15 In real life this is 3.6 for an regular alpha helix
    # The reason for choosing a smaller period is that the helix nicely aligns with its
    # outer edges.
    HELIX_HWIDTH = 90.*11/13 # retro engineered from procheck. Horizontal width in units of degrees on periodic.
    def transformIconToData( self, verts ):
        """Translating the startPoint coordinates from local system x=[0,n] and y=[0,1]
        to axes coordinate system for x and
        to data coordinate system for y.
        """
        for v in verts:
            v[0] += self.startPoint[0]                   # axes coordinates
            v[1] *= self.height
            v[1] += self.startPoint[1]
#            v[1] = scaleAndMove_yValuesFromAxesToData(self.axis, [ v[1] ] )[0]          # data coordinates


#        NTdebug("Vertices icon: %s" % verts)
#        NTdebug("self.startPoint[1]: %s in data system" % self.startPoint[1])
#        NTdebug("self.height: %s in data system" % self.height)

#        for v in verts:
#            v[0] += self.startPoint[0]
#            v[1] *= self.height
#            v[1] += self.startPoint[1]
#        NTdebug("Vertices data: %s" % verts)

    def addPatches(self):
        """Returns True on error.
        # it looks like in procheck a gap of 2 residues makes the next
        # helix start with opposite phase.
        """
        if self.seq < 2: # keep nagging..
            NTcodeerror('Number of helical residues in resList needs to be at least two.')
            return True

        n = self.seq
        # Round the number of turns to halves. Halfturns to ints.
        # n  ht     n   ht
        # 0  error  5   3
        # 1  error  6   3
        # 2  1      7   4
        # 3  2      8   4
        # 4  2      .etc.
        halfTurnsTotal = (n + 1)/ 2
        hw = HelixIconList.HELIX_HWIDTH / 2.
#        NTdebug("halfTurnsTotal: %8.3f ", halfTurnsTotal )
#        NTdebug("hw: %8.3f ", hw )
        # After contemplating for a long time, it seems that the easiest coordinate
        # system to start in is for x [0,360> and on and for y [0,1] due to cyclic
        # nature of the helix.

        s = 270. # starting phase, assume for now we're going down first.
        v = s # jumps 360 after each turn done (at phase: u=0)
        t = s # will keep increasing over the different turns.
        halfTurnsDone=0.0 # number of half turns drawn
        drawnPoly = 0
        while halfTurnsDone < halfTurnsTotal:
            doAtLeastAnotherHalfTurn = (halfTurnsTotal-halfTurnsDone) > 0.5
#            NTdebug("halfTurnsDone           : %f", halfTurnsDone )
#            NTdebug("doAtLeastAnotherHalfTurn: %s", doAtLeastAnotherHalfTurn )
            u = t % 360. # u is in resList [0,360>
            if u == 0 and t != 360.: # v jumps 360 after each turn done (at phase: u=0)
#                NTdebug("Jumping v a full turn ahead, u: %8.3f", v)
                v += 360.
            if u == 90 or s == 270:
                a = [v-hw,        triangular(v)]
                b = [v+hw,        a[1]]
                c = [v-hw+ 90.,   triangular(v+90.)]
                d = [v+hw+ 90.,   c[1]]
                e = [v-hw+180.,   triangular(v+180.)]
                f = [v+hw+180.,   e[1]]
                g = [v-hw+270.,   triangular(v+270.)]
                h = [v+hw+270.,   g[1]]
                i = [v   + 90.,   triangular(hw)]
                j = [v   +270.,   1.-i[1]]

#            NTdebug("plotting poly %d at s,t,u: %8.3f %8.3f %8.3f ", drawnPoly, s,t,u )
#            count = 0
            _allPoints = [ a,b,c,d,e,f,g,h,i,j ] # keep code analysis from complaining.
#            for value in [ a,b,c,d,e,f,g,h,i,j ]:
##                NTdebug(" %2d   %8.3f %8.3f ", count, value[0], value[1] )
#                count += 1
#            if False:
#                verts.append( a,b,c,d,e,f,g,h,i,j ) # keep debugger happy.
#             g h
#             / \-\
#      a_b   /_/j\ \
#       \ \i/e/f
#        \_\ /
#         c d

            verts = NTlist()

            if u == 270.:
                # draw 90 degree segment going down
                verts.append( a,b,d,c )
                t += 90.
                halfTurnsDone += 0.5 # only did 90 degree
            elif u == 0.:
                if doAtLeastAnotherHalfTurn:
                    verts.append( i,d,j,g ) # draw 180 degree segment going up.
                    t += 180.
                    halfTurnsDone += 1.0
                else:
                    verts.append( i,d,f,e )
                    t += 90.
                    halfTurnsDone += 0.5
            elif u == 90.:
                    verts.append( e,f,j,g )
                    t += 90.
                    halfTurnsDone += 0.5
            elif u == 180.:
                if doAtLeastAnotherHalfTurn:
                    cplus = translatePoint(c,360.,0)
                    dplus = translatePoint(d,360.,0)
                    verts.append( g,h,dplus, cplus)
                    t += 180.
                    halfTurnsDone += 1.0
                else:
                    eplus = translatePoint(e,180.,0)
                    fplus = translatePoint(f,180.,0)
                    verts.append( g,h,fplus, eplus )
                    t += 90.
                    halfTurnsDone += 0.5
            else:
                NTerror("in HelixIconList need to improve float comparisons")
                return True

#            NTdebug('verts in local system [(s-hw,s-hw+360*n/4,(0,1)]')
#            NTdebug( vertsToString(verts) )

            # Align left.
            xTranslation = - s + hw
            translate(verts, xTranslation, 0)
#            NTdebug('verts x translated  [(0,360*n/4],(0,1)]')
#            NTdebug( vertsToString(verts) )
            # Expect to see about 4 residues per turn.
            # But we need to compensate for the helix width: HELIX_HWIDTH.
            # E.g. for a full 360 turn we actually will have vertices ranging
            # on the x axis from -hw to 360 + hw.
            # Also need to compensate for when there are e.g. only 3 residue
            # full turn plots.
            totalWidthInDegrees = halfTurnsTotal * 180. + HelixIconList.HELIX_HWIDTH
            xScaleFactor = n/totalWidthInDegrees
            scale(    verts, xScaleFactor, 1)
#            NTdebug('verts almost in icon system  [(0,n),(0,1)]')
#            NTdebug( vertsToString(verts) )

            yScaleFactor = 111./220
            scaleCentered( verts, 1, yScaleFactor)
#            NTdebug('verts in icon system  [(0,n),(0,yScaleFactor)]')
#            NTdebug( vertsToString(verts) )

            self.transformIconToData(verts)
#            NTdebug('verts in axes')
#            NTdebug( vertsToString(verts) )
            p = RangeIconPoly( verts=verts, axis=self.axis, **self.kwargs )
            self.patchList.append(p)
            drawnPoly += 1

class RangeIcon(Polygon):
    """
    A drawing specific for the residue type and in the case of
    amino acids also it's DSSP determined secondary structure
    classification.
        seq is length of icon in residue count.
        startPoint is an x,y tuple lower, left
        width and height are of outer dimensions like startPoint.

        startPoint in data coordinate system now.

        b------c
        |      |
        a------d
"""
    def __init__(self, seq=1, axis=None, startPoint=None, width=1, height=None, **kwargs):
        Patch.__init__(self, **kwargs)
        self.seq = seq
        self.axis= axis
        self.startPoint = startPoint
        self.width = width
        self.height = height
        left, right = startPoint[0], startPoint[0] + width
        bottom, top = startPoint[1], startPoint[1] + height

        a = [left,bottom]
        b = [left,top]
        c = [right,top]
        d = [right,bottom]

        verts = [ a,b,c,d ]
        vertsAsArray = np.asarray(verts, np.float_) #@UndefinedVariable
        self._path = Path(vertsAsArray)
        self.set_closed(True)

#        NTdebug("Created a Rectangle at position %s with width, height: %s, %s" % ( startPoint, width, height ))
#        NTdebug("While axes have extends: %s %s" % (axis.get_xlim(), axis.get_ylim()))

    def transformIconToData( self, verts ):
        """Icon system has a y-axis range of [0,1] and x-axis range of [0,q].
        'data' system has a y-axis range e.g. [-1,6] for the bounding box of the plot. Icons are just above it.
        the x axis is the same at [0,n] for n residues. Always q<n.

        In place operation.
        """
#        NTdebug("Vertices icon: %s" % verts)
#        NTdebug("self.startPoint[1]: %s in data system" % self.startPoint[1])
#        NTdebug("self.height: %s in data system" % self.height)

        for v in verts:
            v[0] += self.startPoint[0]
            v[1] *= self.height
            v[1] += self.startPoint[1]
#        NTdebug("Vertices data: %s" % verts)



class RangeIconPoly(Polygon):
    def __init__(self, verts=None, axis=None, **kwargs):
        Patch.__init__(self, **kwargs)
        self.axis= axis

        vertsAsArray = np.asarray(verts, np.float_) #@UndefinedVariable
        self._path = Path(vertsAsArray)
        self.set_closed(True)

class CoilIcon(RangeIcon):
    """
    Draw an arrow for part of a potential beta stranded sheet.
#
#        b------c
#        |      |
#        a------d
#
        # The x and y coordinates are in data coordinates.
        # The x coordinates are from [0,n] where n is the length of the
        # sequence. Y can have any range.
    """
    COIL_WIDTH = 0.08

    def __init__(self, seq=None, axis=None, startPoint=None, width=None, height=None,**kwargs):
        RangeIcon.__init__(self, seq=seq, axis=axis, startPoint=startPoint, width=width, height=height, **kwargs)

        n = self.seq
        a = [0,0]
        b = [0,1]
        c = [n,1]
        d = [n,0]

        verts = [ a,b,c,d ]
#        NTdebug("Vertices local: %s" % verts)
        scaleCentered(verts, 1., CoilIcon.COIL_WIDTH)
        self.transformIconToData(verts)

        vertsAsArray = np.asarray(verts, np.float_) #@UndefinedVariable
        self._path = Path(vertsAsArray)
        self.set_closed(True)
    # end def
# end class



class StrandIcon(RangeIcon):
    """
    Draw an arrow for part of a potential beta stranded sheet.
    """
    ARROW_WIDTH = 0.6

    def __init__(self, seq=None, axis=None, startPoint=None, width=None, height=None,**kwargs):
        """
        Return the vertices of the icon.
        translating the y coordinate to axes coordinate system.
#               d
#        b------c\
#        |        e
#        a------g/
#               f
        # The y coordinates are in [0,1] first for the maximum resList
        # they can span.
        # The x coordinates are from [0,n] where n is the length of the
        # sequence.
        """
        RangeIcon.__init__(self, seq=seq, axis=axis, startPoint=startPoint, width=width, height=height, **kwargs)

        n = self.seq
        x = (1-StrandIcon.ARROW_WIDTH)/2.
        a = [0,x]
        b = [0,1-x]
        c = [n-1,1-x]
        d = [n-1,1]
        e = [n,.5]
        f = [n-1,0]
        g = [n-1,x]

        verts = [ a,b,c,d,e,f, g ]
        if self.seq == 1: # Just the arrow.
            verts = [ f, d, e ]

#        NTdebug('verts in local system [0-n,0-1]: %s', verts)
        r = 2./3 # from procheck retro engineered
        scaleCentered(verts, 1., r)
#        NTdebug('verts in icon system  [0-n,0-r]:  %s', verts)
        self.transformIconToData(verts)
#        NTdebug('verts in axes                  :  %s', verts)

        vertsAsArray = np.asarray(verts, np.float_) #@UndefinedVariable
        self._path = Path(vertsAsArray)
        self.set_closed(True)
    # end def
# end class




def scaleCentered( verts, xscale, yscale ):
    # Scale a list of vertices by given scale constants with
    # keeping the center of the vertices the same.
    left   = (1.-xscale)/2.
    bottom = (1.-yscale)/2.
    for v in verts:
        v[0] = left   + v[0] * xscale
        v[1] = bottom + v[1] * yscale

def scale( verts, xscale, yscale ):
    # Scale a list of vertices by given scale constants with
    # keeping to the lower left
    for v in verts:
        v[0] *= xscale
        v[1] *= yscale

def translate(verts, xTranslation, yTranslation):
    for v in verts:
        v[0] += xTranslation
        v[1] += yTranslation
    return verts

def translatePoint(v, xTranslation, yTranslation):
    v[0] += xTranslation
    v[1] += yTranslation
    return v


def mapAccessibilityZscore2Color(zScore):
    """
    Returns R,G,B tuple, where R,G,B, resList from 0-1

    White for a zero score.
    Lightgrey for a None score
    Darker blue for a more negative Z score. (-1 is straight blue)
    Darker red for a more positive Z score.  (+1 is straight red)

    The following list contains per-residue Z-scores describing how
    well the residue's observed accessibility fits the expected one.
    A positive Z-score indicates "more exposure than usual", whereas
    a negative Z-score means "more buried than usual".
    |Z-score| must be used to judge the quality.
        """
    if zScore == None:
        return ResPlot.colorBackNoSecStruct
    rangeHi  =  1.
    zScore = limitToRange( zScore, -rangeHi, rangeHi)

    # HSV: Hue, Saturation, Value
    #They all take and return values in the resList [0.0, 1.0]
    hue = ResPlot.hueBlue
    if zScore >= 0:
        hue = ResPlot.hueRed
    saturation = math.fabs( zScore/rangeHi )
    return hsv_to_rgb( hue,saturation*.5,1.   )


def triangularList( xList, c=360. ):
    """Triangular function with periodicity.
    Returns a value between zero and one (inclusive)
    1    /\    /\
        /  \  /  \
    0  /    \/    \
      |  c  |
    c is the cycle period.

    """
    r = []
    for x in xList:
        r.append(triangular(x, c))
    return r

def triangular( x, c=360. ):
    loc = x % c
    phase = loc / c # phase is in resList [0,1>
    if phase <= 0.5:
        return phase * 2.
    return 1. - ((phase-0.5) * 2.)

def vertsToString( verts ):
    result = '\n'
    for v in verts:
        result += "%8.3f %8.3f\n" % (v[0], v[1])
    result = result[:-1] #Remove eol
    return result

def getHeightFromAxis(axis):
    yViewInterval = axis.get_ylim()
    bottom = yViewInterval[0]
    top    = yViewInterval[1]
    height = top-bottom
    return height

def scale_yValuesFromAxesToData(axis, yValueList):
    """Just rescale from axes to data coordinate system.
    E.g. ylim=[-1,9]  input    result
                        0     0
                        0.5   5
    """
    height = getHeightFromAxis(axis)
    result = []
    for v in yValueList:
        r = height * v
        result.append( r )
    # end for
#    NTdebug('scale_yValuesFromAxesToData last y value: %8.3f becomes: %8.3f with bottom,top %8.3f' % (v,r,height) )
    return result

def scaleAndMove_yValuesFromAxesToData(axis, yValueList):
    """Convert y value in axis coordinates [0,1] to
    data coordinates [bottom,top].

    E.g. ylim=[0,10] input    result
                        0     0
                        0.5   5
                        1.1   11
    """
    yViewInterval = axis.get_ylim()
    bottom = yViewInterval[0]
    top    = yViewInterval[1]
    height = top-bottom

    result = []
    for v in yValueList:
        r = bottom + height * v
        result.append( r )
    # end for
#    NTdebug('scaleAndMove_yValuesFromAxesToData last vertex: %8.3f becomes: %8.3f with bottom,top %8.3f,%8.3f' % (v,r,bottom,top) )
    return result


class LocatorResidueMajorTicks(Locator):
    """
    Tick locations are fixed.
    Every starting residue of a chain is a tick, so is every residue
    after a break in the chain. In addition, multiples of 10 are a tick.
    If the total number of residues exceeds 100 then the XXX5 are omitted.
    E.g.
    1brv 171-189 becomes 171, 175, 180, 181, 185
    2hgh 104-193 becomes 104, 110, 120,...   190,191,192,193 (including zn 191-193 in other chains.)
    """
    def __init__(self, ranges):
        self.locs = []
        totalNumberResidues = len(ranges)

        doFives = True
        if totalNumberResidues/100. > 1:
            doFives = False

        idx = -0.5 # Shift so that the first ticked label drawn is not at 1 but at 0.5
        lastResNum = None
        lastChainName = None
        for res in ranges:
            # detect a break
            isBroken = False
            if lastResNum == None:
                isBroken = True
            elif res.resNum != lastResNum + 1:
                isBroken = True
            elif res.chain.name != lastChainName:
                isBroken = True

            lastResNum    = res.resNum
            lastChainName = res.chain.name

            idx += 1
#                if (not res.resNum%10) or (doFives and (not res.resNum%5)):
            if (isBroken or
                not res.resNum%10 or
                (doFives and not res.resNum%5)):
                self.locs.append(idx)
#                NTdebug('Adding at resNum %s, idx: %s'%(res.resNum,idx ))

    def __call__(self):
        return self.locs


class MultipleLocatorByOffset(MultipleLocator):
    """
    Set a tick -next to- every integer that is multiple of base in the
    viewInterval
    """

    def __init__(self, base=1.0, offset=-0.5):
        MultipleLocator.__init__(self, base)
        self.offset = offset

    def __call__(self):
        'Return the locations of the ticks'

        try:
            self.verify_intervals()
            vmin, vmax = self.viewInterval.get_bounds()
        except:
            vmin, vmax = self.axis.get_view_interval()

        if vmax<vmin:
            vmin, vmax = vmax, vmin
        vmin = self._base.ge(vmin)
        start = vmin+self.offset
        stop  = vmax+self.offset+0.001*self._base.get_base()
        locs =  frange(start,stop, self._base.get_base())

        return locs

#class LocatorByOffset(MaxNLocator):
#    def bin_boundaries(self, vmin, vmax):
#        nbins = self._nbins
#        scale, offset = scale_range(vmin, vmax, nbins)
#        if self._integer:
#            scale = max(1, scale)
#        vmin -= offset
#        vmax -= offset
#        raw_step = (vmax-vmin)/nbins
#        scaled_raw_step = raw_step/scale
#
#        for step in self._steps:
#            if step < scaled_raw_step:
#                continue
#            step *= scale
#            best_vmin = step*divmod(vmin, step)[0]
#            best_vmax = best_vmin + step*nbins
#            if (best_vmax >= vmax):
#                break
#        if self._trim:
#            extra_bins = int(divmod((best_vmax - vmax), step)[0])
#            nbins -= extra_bins
##was    return (arange(nbins+1) * step + best_vmin + offset)
#        return (arange(nbins+1) * step + best_vmin + offset -.5)

class FormatResTypesFormatter(Formatter):
    def __init__(self, molecule):
        self.molecule = molecule
        self.resPropList = ['Z'] # The zero is not supposed to be used.
        for res in molecule.allResidues():
            resProp = 'x'
            if res.shortName:
                resProp = res.shortName
            else:
                resProp = res.name

            if ( res.hasProperties('nucleic') and
                (resProp[0]=='r' or resProp[0]=='d') and
                len(resProp)>1):
                resProp = resProp[1:2] # truncate rc to c
            else:
                resProp = resProp[0:1] # truncate A171 to A

            self.resPropList.append(resProp.upper())
#        NTdebug("FormatResTypesFormatter initialized with: %s" % self.resPropList )

    def __call__(self, x, pos=None):
        'Return the one character residue type for tick val x at position pos'
#        NTdebug('called with x,pos: %s, %s' %(x,pos))
        if pos > 0 and pos < len(self.resPropList):
            return self.resPropList[pos]
        return 'X'

class FormatResNumbersFormatter(Formatter):
    def __init__(self, range):
        self.resPropList = ['Z'] # The zero is not supposed to be used.
        prevChainId = None
        for res in range:
            if res.chain.name != prevChainId:
                prevChainId = res.chain.name
                self.resPropList.append(res.chain.name +`res.resNum`)
            else:
                self.resPropList.append(                `res.resNum`)

    def __call__(self, x, pos=None):
        'Return the one character residue type for tick val x at position pos'
#        NTdebug('FormatResNumbersFormatter called with x,pos: %s, %s' %(x,pos))
        xint = int(x+0.5)
        if xint > 0 and xint < len(self.resPropList):
            return self.resPropList[xint]
        return 'X'



def removeNulls(serie):
    """Check y values for None and kick them out if they are."""
    result = []
    for point in serie:
        if point[1] == None:
            NTdebug("Kicking point with None y at x: %s", point[0] )
            continue
        result.append( point )
    return result

def integerNumberOnly(x,_dummy):
    'Returns empty string wherever not integer x'
    remainder = math.fabs(x) % 1.0
    if remainder > 0.001:
        return ''
    return '%.0f' % x
