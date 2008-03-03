from cing.Libs.NTplot import NTplot
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import limitToRange
from cing.PluginCode.Whatif import INOCHK_STR
from cing.PluginCode.Whatif import VALUE_LIST_STR
from cing.PluginCode.Whatif import WHATIF_STR
from cing.PluginCode.procheck import CONSENSUS_SEC_STRUCT_FRACTION
from cing.PluginCode.procheck import PROCHECK_STR
from cing.PluginCode.procheck import SECSTRUCT_STR
from colorsys import hsv_to_rgb
from pylab import * # preferred importing. Includes nx imports. #@UnusedWildImport
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTcodeerror
from cing.Libs.NTutils import NTlist



if not NTplot.useMatPlotLib:
    raise "need to use matplotlib for resPlot"

"""
x coordinate is in 'data' coordinate system (sequence number)
y coordinate is in axis coordinates (from 0 to 1) when the renderer asks for the
    coordinate a conversion needs to take place.
"""
class ResPlot(NTplot):
    """Plot class for sequence of residues"""

    SMALLEST_HELIX_LENGTH = 2
    
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
    resPerPlot    = 100 # Number of residues per plot"""
    
    hueRed  = 0.
    hueBlue = 0.68
    
    def __init__(self,**kwargs):
        """seq        Residue list for which to produce plots
        """
        NTplot.__init__(self, **kwargs)
        self.xLabel = 'Sequence'
        self.resIconHeight =  1.
        
    def getsecStructElementList(self):
        """Chop the molecule into segments of the same secondary structure type
        from consensus Procheck attribute.
        
        ' HHHHH   SSSS   ' becomes
        [ ' ', 'HHHH', '   ', 'SSSS, '   ' ] but then in residue objects.
        """
        if not self.has_key('molecule'):
            NTerror('in ResPlot: need a molecule')
            return True
        r=[]
        for ch in self.molecule.allChains():
            NTdebug('getsecStructElementList chain: %s', ch)
            range = []
            prevSecStruct = None
            for res in ch.allResidues():
                secStructList = res.getDeepByKeys(PROCHECK_STR,SECSTRUCT_STR)
                NTdebug( 'secStructList before reduced to 3 states: %s', secStructList )
                secStructList = to3StateUpper( secStructList )
                if secStructList:
                    secStruct = secStructList.getConsensus(CONSENSUS_SEC_STRUCT_FRACTION) # will set it if not present yet.
                else:
                    secStruct = None
                NTdebug('getsecStructElementList res: %s %s %s', res, secStructList, secStruct)
                if prevSecStruct != secStruct:
                    if range:
                        r.append(range)
                    range=[]
                range.append(res)
                prevSecStruct=secStruct                    
            if range:
                r.append(range)
        NTdebug('getsecStructElementList result: %s', r)
        return r
    
    def drawResIcons(self):
        kwargs = {'edgecolor':ResPlot.colorLine, 'facecolor':ResPlot.colorHelixIn, 'clip_on':None}

        ax = gca()
        resList = self.molecule.allResidues()
        if not resList():
            return True
        if len(resList) > ResPlot.resPerPlot: # Truncate for now.
            resList = resList[:ResPlot.resPerPlot+1]
        seqLength = len(resList)
                
        ySpaceAxis    = 0.02      # axis, the vertical open area between elements.
#        yIconSpaceAxis= 0.005     # axis, the vertical open area from within box

        iconBoxXstart = 0              # data
        iconBoxXwidth = seqLength      # data 
        iconBoxYstart = 1 + ySpaceAxis # axis
        iconBoxYheight= 0.06           # axis
        
        self.xRange       = (0,iconBoxXwidth)   # x-axis (min,max) tuple, None is autoscale
         
        # Get a background with Z-scores of accessibility.
        i = 0 
        for res in resList:
            accessibilityZscoreList = res.getDeepByKeys(WHATIF_STR,INOCHK_STR,VALUE_LIST_STR)
#            NTdebug('accessibilityZscoreList: %s', accessibilityZscoreList)
            if not accessibilityZscoreList:
                accessibilityZscore = None
            else:
                accessibilityZscore = accessibilityZscoreList.average()[0]
            color = mapAccessibilityZscore2Color(accessibilityZscore) # get an rgb tuple
            xy = ( iconBoxXstart + i, iconBoxYstart)
#            NTdebug("color: %8s %-80s" % (accessibilityZscore, color))
            p = RangeIcon( seq=1,xy=xy,width=1,height=iconBoxYheight,
                           edgecolor=color, facecolor=color, clip_on=None)
            ax.add_patch(p)            
            i += 1       
        
        # Get a icons for secondary structure
        secStructElementList = self.getsecStructElementList()
        i = 0 
        for element in secStructElementList:
#            NTdebug(`element`)
            elementLength = len(element)
            res = element[0]
            secStructList = res.getDeepByKeys(PROCHECK_STR,SECSTRUCT_STR)
            secStructList = to3StateUpper( secStructList )
            if secStructList:
                secStruct = secStructList.getConsensus(CONSENSUS_SEC_STRUCT_FRACTION) # will set it if not present yet.
            else:
                secStruct = None
            if secStruct == 'H' and elementLength < 2: # Can't plot a helix of length 1 residue
                secStruct = None
            if secStruct == ' ':
                secStruct = None
            NTdebug('secStruct res: %s %s %s', res, secStructList, secStruct)

            xy = ( iconBoxXstart + i, iconBoxYstart)
            width = elementLength
            
            rangeIconList = RangeIconList( secStruct=secStruct,seq=elementLength,xy=xy,width=width,height=iconBoxYheight,**kwargs)
            if rangeIconList.addPatches():
                NTerror("Failed to addPatches for element with residues: %s", element)
                continue
            for p in rangeIconList.patchList:
                ax.add_patch(p)        
            i += elementLength
        
    

class RangeIconList():
    def __init__(self, secStruct=' ', seq=1, xy=None, width=None, height=None,
                 **kwargs):
        self.patchList= []
        self.seq      = seq
        self.secStruct= secStruct
        self.xy       = xy
        self.width    = width
        self.height   = height
        self.kwargs   = kwargs
            
    def addPatches(self):
        "Return True on error"
        NTmessage("Doing addPatches for seq: %d", self.seq)
        
        if self.secStruct=='S':
            p = StrandIcon(self.seq, self.xy, self.width, self.height,**self.kwargs)
            if not p:
                NTerror("Failed to create StrandIcon")
                return True
            self.patchList.append( p )
        elif self.secStruct=='H':
            helixIconList = HelixIconList(seq=self.seq, xy=self.xy, width=self.width, height=self.height,**self.kwargs)
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
            p = CoilIcon(self.seq, self.xy, self.width, self.height,**self.kwargs)
            if not p:
                NTerror("Failed to create CoilIcon")
                return True
            self.patchList.append( p )
        else:
            NTerror("Failed to find one of 3 states, doing addPatches for seq: %d and self.secStruct: %s", (self.seq, self.secStruct))
            return True
    
class HelixIconList(RangeIconList):
    """ Draw helices in half turn increments scale back x-coordinate to fit odd
        numbered residue helices.    """
        
    def __init__(self, seq=2, xy=None, width=None, height=None, phaseUp=True,
                 **kwargs
                 ):
        RangeIconList.__init__(self, seq=seq, xy=xy, width=width, height=height, **kwargs)    
        self.phaseUp = phaseUp
        NTdebug('In HelixIconList.__init__: seq: %d', self.seq)
            
    def toAxes( self, verts ):
        """Translating the xy coordinates from local system x=[0,n] and y=[0,1] 
        to axes coordinate system for x and
        to data coordinate system for y.
        """
        for v in verts:
            v[0] += self.xy[0]                   # axes coordinates
            v[1] *= self.height
            v[1] += self.xy[1]          
            l    = [ v[1] ]
            v[1] = convert_yunits(l)[0]          # data coordinates

    def addPatches(self):
        """Returns True on error.
        # it looks like in procheck a gap of 2 residues makes the next
        # helix start with opposite phase.  
        """
        if self.seq < 2: # keep nagging..
            NTcodeerror('Number of helical residues in range needs to be at least two.')
            return True
        
        HELIX_HWIDTH = 90.*11/13 # retro engineered from procheck. Horizontal width in units of degrees on periodic.
#        HELIX_PERIOD = 4.- HELIX_HWIDTH # 3.15 In real life this is 3.6 for an regular alpha helix
        # The reason for choosing a smaller period is that the helix nicely aligns with its 
        # outer edges. 
        n = self.seq
        # Round the number of turns to halves. Halfturns to ints.
        # n  ht     n   ht
        # 0  error  5   3
        # 1  error  6   3
        # 2  1      7   4
        # 3  2      8   4
        # 4  2      .etc.
        halfTurnsTotal = (n + 1)/ 2
        hw = HELIX_HWIDTH / 2.
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
            u = t % 360. # u is in range [0,360>
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
            count = 0
            for value in [ a,b,c,d,e,f,g,h,i,j ]:
#                NTdebug(" %2d   %8.3f %8.3f ", count, value[0], value[1] )
                count += 1
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
            totalWidthInDegrees = halfTurnsTotal * 180. + HELIX_HWIDTH
            xScaleFactor = n/totalWidthInDegrees
            scale(    verts, xScaleFactor, 1)
#            NTdebug('verts almost in icon system  [(0,n),(0,1)]')
#            NTdebug( vertsToString(verts) )

            yScaleFactor = 111./220 
            scaleCentered( verts, 1, yScaleFactor)
#            NTdebug('verts in icon system  [(0,n),(0,yScaleFactor)]')
#            NTdebug( vertsToString(verts) )

            self.toAxes(verts)
#            NTdebug('verts in axes')
#            NTdebug( vertsToString(verts) )
            p = RangeIconPoly( xy=verts, **self.kwargs )            
            self.patchList.append(p)
            drawnPoly += 1
        
class RangeIcon(Rectangle):
    """A drawing specific for the residue type and in the case of
    amino acids also it's DSSP determined secondary structure
    classification.
        seq is length of icon in residue count.
        xy is an x,y tuple lower, left
        width and height are of outer dimensions like xy.
    """
    def __init__(self, seq=1, xy=None, width=None, height=None,
                 **kwargs
                 ):        
        Rectangle.__init__(self, xy=xy, width=width, height=height, **kwargs)
        self.seq = seq
        
    def toAxes( self, verts ):
        """See namesake
        """
        for v in verts:
            v[0] += self.xy[0]
            v[1] *= self.height
            v[1] += self.xy[1] 
            l    = [ v[1] ]
            v[1] = convert_yunits(l)[0]     

    def get_verts(self):
        """
        Return the vertices of the icon.
        translating the y coordinate from axes coordinate system to
        data coordinate system.
        """        
        self.set_clip_on(None) # weird that this needs to be called this low in the code.

        x, y = self.xy
        left, right = self.convert_xunits((x, x + self.width))
        bottom, top = convert_yunits((y, y + self.height))
        verts = ( (left,  bottom), 
                  (left,  top),
                  (right, top),   
                  (right, bottom) ) 
#        NTdebug('xy   : %s', self.xy)
#        NTdebug(' self.width   : %s',  self.width)
#        NTdebug(' self.height  : %s',  self.height)
#        NTdebug('verts: %s', verts)
        return verts
        
class RangeIconPoly(Polygon):
    def get_verts(self):
        """
        Return the vertices of the icon.
        translating the y coordinate to axes coordinate system.
        xy is a sequence of (x,y) 2 tuples
        
        """        
        self.set_clip_on(None) # weird that this needs to be called this low in the code.

        xs, ys = zip(*self.xy)[:2]
        xs = self.convert_xunits(xs)
        ys =      convert_yunits(ys)
        return zip(xs, ys)

class CoilIcon(RangeIcon):
    """
    Draw an arrow for part of a potential beta stranded sheet.
    """
    def __init__(self, seq, xy=None, width=None, height=None,
                 **kwargs
                 ):     
        RangeIcon.__init__(self, seq=seq, xy=xy, width=width, height=height, **kwargs)    
    def get_verts(self):
        """
        Return the vertices of the icon.
        translating the y coordinate to axes coordinate system.
#               
#        b------c
#        |      | 
#        a------d
#               
        # The y coordinates are in [0,1] first for the maximum range 
        # they can span.
        # The x coordinates are from [0,n] where n is the length of the 
        # sequence.
        """        
        self.set_clip_on(None) # weird that this needs to be called this low in the code.
        COIL_WIDTH = 0.08    
        n = self.seq
        a = [0,0]
        b = [0,1]
        c = [n,1]
        d = [n,0]

        verts = [ a,b,c,d ]        
#        NTdebug('verts in local system [0-n,0-1]: %s', verts)
        scaleCentered(verts, 1., COIL_WIDTH)
#        NTdebug('verts in icon system  [0-n,0-r]:  %s', verts)
        self.toAxes(verts)
#        NTdebug('verts in axes                  :  %s', verts)
        return verts
        
        
class StrandIcon(RangeIcon):
    """
    Draw an arrow for part of a potential beta stranded sheet.
    """
    def __init__(self, seq, xy=None, width=None, height=None,
                 **kwargs
                 ):        
        RangeIcon.__init__(self, seq=seq, xy=xy, width=width, height=height, **kwargs)    
        NTdebug('In StrandIcon.__init__: one strand seq: %d', self.seq)

    def get_verts(self):
        """
        Return the vertices of the icon.
        translating the y coordinate to axes coordinate system.
#               d
#        b------c\
#        |        e
#        a------g/
#               f
        # The y coordinates are in [0,1] first for the maximum range 
        # they can span.
        # The x coordinates are from [0,n] where n is the length of the 
        # sequence.
        """        
        self.set_clip_on(None) # weird that this needs to be called this low in the code.
        ARROW_WIDTH = 0.6    
        n = self.seq
        x = (1-ARROW_WIDTH)/2.
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
        self.toAxes(verts)
#        NTdebug('verts in axes                  :  %s', verts)
        return verts
        


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
    Returns R,G,B tuple, where R,G,B, range from 0-1

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
    #They all take and return values in the range [0.0, 1.0]
    hue = ResPlot.hueBlue
    if zScore >= 0:            
        hue = ResPlot.hueRed
    saturation = math.fabs( zScore/rangeHi )    
    return hsv_to_rgb( hue,saturation*.5,1.   )

    
def convert_yunits(yValueList):
    """ Convert from value in y-axis coordinates [0,1] to
    data coordinates [bottom,top].
    
    E.g. ylim=[0,10] input    result
                        0     0
                        0.5   5
                        1.1   11
    """
    ax = gca()
    yViewInterval = ax.get_ylim()
    bottom = yViewInterval[0]
    top    = yViewInterval[1]
    height = top-bottom

    result = []
    for v in yValueList:
        result.append( bottom + height * v )
    return result

def triangularList( xList, c=360. ):
    """Triangular function with periodicity. 
    Returns a value between zero and one (inclusive)
  1      /\    /\
        /  \  /  \
  0    /    \/    \
      |  c  |
      c is the cycle period.
      
      """
    r = []
    for x in xList:
        r.append(triangular(x, c))
    return r

def triangular( x, c=360. ):
    loc = x % c
    phase = loc / c # phase is in range [0,1>
    if phase <= 0.5:
        return phase * 2.
    return 1. - ((phase-0.5) * 2.)

def vertsToString( verts ):
    result = '\n'
    for v in verts:
        result += "%8.3f %8.3f\n" % (v[0], v[1])
    result = result[:-1] #Remove eol
    return result

def to3StateUpper( strNTList ):
    result = NTlist()
    for c in strNTList:
        if c in ' HShs':
            result.append( string.upper(c))
        else:
            result.append( ' ' )
    return result