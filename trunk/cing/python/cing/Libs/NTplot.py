import NTutils
import math

haveBiggles = False
try:
    import biggles
    haveBiggles = True
except ImportError:
    pass

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

class NTplot( NTutils.NTdict ):
    """
    Base plotting class
    """

    def __init__( self, **kwds ):
        NTutils.NTdict.__init__( self )
        self.__CLASS__    = 'NTplot'

        self.screenSize   = (500,500)
        self.hardcopySize = (400,400)
        self.font         = 'Helvetica'

        self.title        = None
        self.xLabel       = None
        self.yLabel       = None

        self.aspectRatio  = 1.0    # Aspect ratio
        self.xRange       = None   # x-axis (min,max) tuple, None is autoscale
        self.yRange       = None   # y-axis (min,max) tuple, None is autoscale

        self.xTicks       = None   # x-axis tics-list, None is autotics
        self.yTicks       = None   # y-axis tics-list, None is autotics

        self.xAxis        = True
        self.yAxis        = True

        self.xGrid        = True   # x-axis grid toggle
        self.yGrid        = True   # y-axis grid toggle

        self.update( kwds )

        if (not haveBiggles):
            NTutils.NTerror("NTplot.__init__: No biggles\n")
        else:
            #initialise the biggles plot
            biggles.configure('persistent','no')
            self.b = biggles.FramedPlot()
            self.move( (0.0, 0.0) )
        #endif
    #end def

    def move( self, point ):
        self.currentPoint = point
    #end def

    def draw( self, endPoint, attributes=None ):
        if attributes == None: attributes = defaultAttributes
        self.b.add(
            biggles.Curve( [self.currentPoint[0], endPoint[0]],
                           [self.currentPoint[1], endPoint[1]],
                           linetype  = attributes.lineType,
                           linewidth = attributes.lineWidth,
                           linecolor = attributes.lineColor
                         )
        )
        self.currentPoint = endPoint
    #end def

    def line( self, startPoint, endPoint, attributes=None):
        self.move( startPoint )
        self.draw( endPoint=endPoint, attributes=attributes )
    #end def

    def lines( self, points, attributes=None ):
        if len(points) == 0: return
        self.move( points[0] )
        for p in points[1:]:
            self.draw( endPoint=p, attributes=attributes )
        #end for
    #end def

    def box( self, point, sizes, attributes=None ):
        if attributes == None: attributes = defaultAttributes
        self.move(  point )
        # clockwise
        #  p2---p3
        #   |   |
        #  p1---p4
        p1 = point
        p2 = (point[0],          point[1]+sizes[1])
        p3 = (point[0]+sizes[0], point[1]+sizes[1])
        p4 = (point[0]+sizes[0], point[1])

#        self.closedObject( [p1,p2,p3,p4], attributes )
        if attributes.fill:
            self.b.add(
                biggles.FillBetween( [p1[0], p2[0], p3[0]],
                                     [p1[1], p2[1], p3[1]],
                                     [p1[0], p4[0], p3[0]],
                                     [p1[1], p4[1], p3[1]],
                                     fillcolor = attributes.fillColor
                                   )
            )
        #end if
        if attributes.line:
            self.draw( p2, attributes )
            self.draw( p3, attributes )
            self.draw( p4, attributes )
            self.draw( p1, attributes )
        #end if
    #end def

    def point( self, point, attributes=None ):
        """
            Add a point
            add xErrorBar if len(points)>2
            add yErrorBar if len(points)>3
        """
        if attributes == None: attributes = defaultAttributes
        self.move(  (point[0],point[1]) )
        self.b.add(
           biggles.Point( point[0], point[1],
                          symboltype = attributes.pointType,
                          symbolsize = attributes.pointSize,
                          color      = attributes.pointColor
                        )
        )
        if (len(point) > 2 and point[2] >= 0.0):
            self.b.add(
                biggles.SymmetricErrorBarsX( [point[0]], [point[1]], [point[2]],
                                             color = attributes.pointColor
                                           )
            )
        #end if
        if (len(point) > 3 and point[3] >= 0.0):
            self.b.add(
               biggles.SymmetricErrorBarsY( [point[0]], [point[1]], [point[3]],
                                             color = attributes.pointColor
                                          )
            )
        #end if
    #end def

    def points( self, points, attributes=None ):
        if len(points) == 0: return
        for p in points:
            self.point( p, attributes )
        #end for
    #end def

    def label( self, point, text, attributes=None ):
        if attributes == None: attributes = defaultAttributes
        self.b.add(
            biggles.DataLabel( point[0], point[1], text,
                               fontface = attributes.font,
                               fontsize = float(attributes.fontSize)/4.0,
                               texthalign = attributes.textAlign,
                               color = attributes.fontColor
                             )
        )
    #end def

    def labeledPoint( self, point, text, attributes=None ):
        self.point( point, attributes )
        self.label( point, text, attributes )
    #end def

    def autoScale( self, x=True, y=True ):
        if x: self.xRange = None
        if y: self.yRange = None
    #end def

    def updateSettings( self ):
        #update settings
        self.b.title         = self.title
        self.b.xlabel        = self.xLabel
        self.b.ylabel        = self.yLabel

        self.b.x.draw_axis   = self.xAxis
        self.b.y.draw_axis   = self.yAxis
        self.b.x2.draw_ticks = 0
        self.b.y2.draw_ticks = 0
        self.b.x.tickdir     = 1
        self.b.y.tickdir     = 1

        self.b.x.ticks       = self.xTicks
        self.b.y.ticks       = self.yTicks

        self.b.aspect_ratio  = self.aspectRatio
        self.b.xrange        = self.xRange
        self.b.yrange        = self.yRange

        self.b.x.draw_grid   = self.xGrid
        self.b.y.draw_grid   = self.yGrid

        biggles.configure('width',    self.screenSize[0] )
        biggles.configure('height',   self.screenSize[1] )
        biggles.configure('fontface', self.font)

    #end def

    def show( self ):
        self.updateSettings()
        self.b.show()
    #end def

    def hardcopy( self, fileName, graphicsFormat = 'png' ):
        self.updateSettings()
        self.b.write_img( graphicsFormat, self.hardcopySize[0], self.hardcopySize[1], fileName )
    #end def


    def histogram( self, theList, low, high, bins, leftMargin=0.05, rightMargin=0.05, attributes=None ):
        his = NTutils.NThistogram( theList, low, high, bins )
        self.his = his

        self.maxY = max(his)

        for bin in range( bins ):
            if his[bin] > 0:
                self.box( point = ( his.low+(bin+leftMargin)*his.binSize, 0.0 ),
                          sizes = ( his.binSize*(1.0-(leftMargin+rightMargin)), float(his[bin]) ),
                          attributes = attributes
                        )
            #end if
        #end for
    #end def

    def barChart( self, barList, leftMargin=-0.5, rightMargin=0.5, attributes=None ):
        """
        Plot a bars at x-leftMargin to x+rightMargin, y height

        barList: list of (x, y) tuples
        """

        for x,y in barList:
            if y != 0.0:
                self.box( point = ( x+leftMargin, 0.0 ),
                          sizes = ( rightMargin-leftMargin, float(y) ),
                          attributes = attributes
                        )
            #end if
        #end for
    #end def

#end class

#-----------------------------------------------------------------------------
# Plotting attributes
#-----------------------------------------------------------------------------

def NTplotAttributes( **kwds ):
    a = NTutils.NTdict()

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
                      'textAlign:  %(textAlign)s\n'

    # line defaults
    a.lineType   = 'solid'
    a.lineColor  = 'black'
    a.lineWidth  = 1.0

    # box
    a.fill       = True
    a.fillColor  = 'black'
    a.line       = False

    # points
    a.pointType  = 'circle'
    a.pointSize  = 2.0
    a.pointColor = 'blue'

    # fonts
    a.font       = 'Helvetica'
    a.fontSize   = 12
    a.fontColor  = 'black'

    # text
    a.textAlign  = 'left'

    # update
    a.update( kwds )

    return a
#end def

def lineAttributes( type='solid', width=1.0, color='black' ):
    return NTplotAttributes( lineType=type, lineWidth=width, lineColor=color )
#end def

def boxAttributes( fill=True, fillColor='black', line=False, lineColor='black' ):
    return NTplotAttributes( lineType='solid', lineColor=lineColor, line=line,
                             fill=fill, fillColor=fillColor
                           )
#end def

def fontAttributes( font='Helvetica', size=12, color='black' ):
    return NTplotAttributes( font=font, fontSize=size, fontColor=color )
#end def

def pointAttributes( type='circle', size=2.0, color='black' ):
    return NTplotAttributes( pointType=type, pointSize=size, pointColor=color )
#end def

# Some default attributes
defaultAttributes  = NTplotAttributes()

solidLine          = lineAttributes( type='solid',      width=1.0, color='black' )
dottedLine         = lineAttributes( type='dotted',     width=1.0, color='black' )
dashedline         = lineAttributes( type='longdashed', width=1.0, color='black' )
redLine            = lineAttributes( type='solid',      width=1.0, color='red' )
blueLine           = lineAttributes( type='solid',      width=1.0, color='blue' )
greenLine          = lineAttributes( type='solid',      width=1.0, color='green' )

blackBox           = boxAttributes( fill=True,  fillColor='black' )
redBox             = boxAttributes( fill=True,  fillColor='red' )
greenBox           = boxAttributes( fill=True,  fillColor='green' )
openBox            = boxAttributes( fill=False, fillColor='black', line=True, lineColor='black' )

plusPoint          = pointAttributes( type='plus',          size=2.0, color='blue' )
circlePoint        = pointAttributes( type='circle',        size=2.0, color='blue' )
filledCirclePoint  = pointAttributes( type='filled circle', size=2.0, color='blue' )

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

#-----------------------------------------------------------------------------
# Testing from here-on
#-----------------------------------------------------------------------------
#
if __name__ == '__main__':
    pass

    p = NTplot( title = 'test', xRange=(0,10), yRange=(0,10), xLabel='aap' )

#     p.line( (0,0), (3,2) )
#     p.draw( (5,1), p.dottedLine )
#
#     p.move( (0,0) )
#     for i in range(0,11):
#         p.draw( (i,i*i), lineAttributes( lineColor=strRgb( i, 0,10) ) )
#     #end for
#
#     x = []
#     y = []
#     for t in range(0,361):
#         x.append( math.cos(float(t)/180.0*math.pi) )
#         y.append( math.sin(float(t)/180.0*math.pi) )
#     #end for
#     p.lines( map(None, x, y), p.blueLine )
    p.box( (1,0), (0.9,2), boxAttributes( lineColor='black', line=True, fillColor='blue', fill=True) )
    p.box( (2,0), (0.9,5), boxAttributes( lineColor='black', line=True, fillColor='blue', fill=True) )
    p.point( (3,3.5,0,1), pointAttributes(color='red') )

    p.point( (7,6,0,2), plusPoint(pointColor='green', fontColor='red', font='Courier') )
    p.label( (7,6), 'label', plusPoint)
    p.line( (5,1), (10,0), greenLine )

    p.labeledPoint( (5,5), 'point 5' )

    x=[3,5,6,2,8,9,4,5]
    y=[5,2,3,1,7,8,6,3]
    ey=[0.1,0.2,0.5,0,0.2,0.1]

    p.points(map(None,x,y,NTutils.NTfill(0.0,len(x)), ey))
    p.show()
