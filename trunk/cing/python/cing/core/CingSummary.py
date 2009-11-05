from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTlist
from cing.Libs.NTutils import NTvalue
from cing.Libs.NTutils import XML2obj
from cing.Libs.NTutils import XMLhandler
from cing.Libs.NTutils import obj2XML
from cing.Libs.fpconst import NaN
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.core.parameters import plugins
import cing
import os

class CingSummary( NTdict ):
    """
    Simple class to store CING summary result as a dict for easy retrieval
    """

    def __init__( self ):
        NTdict.__init__( self,
                         __CLASS__           = 'CingSummary',

                         version             = cing.cingVersion,

                         name                = None,

                         totalResidueCount   = 0,
                         proteinResidueCount = 0,
                         nucleicResidueCount = 0,

                         # CING scores in %
                         CING_red            = NaN,
                         CING_orange         = NaN,
                         CING_green          = NaN,
                         CING_residueROG     = NTlist(),

                         # Procheck scores
                         PC_core            = NaN,
                         PC_allowed         = NaN,
                         PC_generous        = NaN,
                         PC_disallowed      = NaN,
                         PC_gf              = None,

                         # WHATIF scores done again later; just here to make sure for the format statement
                         WI_ramachandran    = None,
                         WI_bbNormality     = None,
                         WI_rotamer         = None,

                         distances          = NTlist(),
                         dihedrals          = NTlist(),
                         rdcs               = NTlist(),

                        # single line format
                         __FORMAT__ = '%(name)-10s   ' +\
                                      'RESIDUES: tot %(totalResidueCount)3d  prot %(proteinResidueCount)3d  nucl %(nucleicResidueCount)3d   ' +\
                                      'ROG(%%): %(CING_red)5.1f %(CING_orange)5.1f %(CING_green)5.1f    ' +\
                                      'PROCHECK(%%): %(PC_core)5.1f %(PC_allowed)5.1f %(PC_generous)5.1f %(PC_disallowed)5.1f  gf: %(PC_gf)-15s  ' +\
                                      'WHATIF: rama %(WI_ramachandran)-15s bb %(WI_bbNormality)-15s rotamer %(WI_rotamer)-15s '

                    )
        if hasattr(plugins, WHATIF_STR) and plugins[ WHATIF_STR ].isInstalled:
            from cing.PluginCode.Whatif import Whatif
            # Add all Whatif summary check Id's
            # The below causes an exception when called on a system that has no Whatif.
            for checkId in Whatif.summaryCheckIdList:
                key = 'WI_' + Whatif.cingCheckId(checkId)
                self[key] = None
        #end if

        self.saveAllXML()
    #end def

    def getSummaryFromProject( self, project ):
        """
        Extract the data from project
        """

        self.name = project.name

        # Residue counts (total, protein, nucleic)
        self.totalResidueCount   = len( project.molecule.allResidues() )
        proteinResidues = project.molecule.residuesWithProperties('protein' )
        self.proteinResidueCount = len( proteinResidues )
        nucleicResidues = project.molecule.residuesWithProperties('nucleic' )
        self.nucleicResidueCount = len( nucleicResidues )

        # ROG scores
        rog = NTlist( 0, 0, 0 ) # Counts for red, orange, green.
        for residue in project.molecule.allResidues():
            if residue.rogScore.isRed():
                rog[0] += 1
            elif residue.rogScore.isOrange():
                rog[1] += 1
            else:
                rog[2] += 1
            self.CING_residueROG.append( (residue._Cname(-1), residue.rogScore) )
        #end for
        total = reduce(lambda x, y: x+y+0.0, rog) # total expressed as a float because of 0.0
        for i, _x in enumerate(rog): rog[i] = rog[i]*100.0/total
        self.CING_red    = round(rog[0],1)
        self.CING_orange = round(rog[1],1)
        self.CING_green  = round(rog[2],1)

        # Procheck (core, allowed,  generous, disallowed) (%), average g_factor
        if self.proteinResidueCount > 0 and project.molecule.has_key('procheck') and project.molecule.procheck and project.molecule.procheck.summary:
            self.PC_core       = project.molecule.procheck.summary.core
            self.PC_allowed    = project.molecule.procheck.summary.allowed
            self.PC_generous   = project.molecule.procheck.summary.generous
            self.PC_disallowed = project.molecule.procheck.summary.disallowed
            self.PC_gf  = proteinResidues.zap('procheck','gf').average2(fmt='%6.3f +/- %5.3f')
        #end if

        # Whatif
        if hasattr(plugins, WHATIF_STR) and plugins[ WHATIF_STR ].isInstalled:
            from cing.PluginCode.Whatif import Whatif
            if self.proteinResidueCount > 0 and project.whatifStatus.completed and project.whatifStatus.parsed:
                for checkId in Whatif.summaryCheckIdList:
                    if project.molecule[WHATIF_STR].has_key(checkId):
                        key = 'WI_' + Whatif.cingCheckId(checkId)
                        self[key] = project.molecule[WHATIF_STR][checkId].average(fmt='%6.3f +/- %5.3f')
            #end if
        #end if

        for drl in project.distances:
            self.distances.append( self.distanceRestraintListToTuple(drl) )

        for drl in project.dihedrals:
            self.dihedrals.append( self.dihedralRestraintListToTuple(drl) )

        return self
    #end def

    def distanceRestraintListToTuple(self, drl):
        """Return a single tuple of relevant results ed.
        """
        return (drl.name, drl.status,
                len(drl), len(drl.intraResidual), len(drl.sequential),len(drl.mediumRange),len(drl.longRange),len(drl.ambigious),
                NTvalue(drl.rmsdAv, drl.rmsdSd, fmt='%.4f +/ %.4f'), drl.violCountLower, drl.violCount1, drl.violCount3, drl.violCount5, str(drl.rogScore)
               )
    #end def

    def dihedralRestraintListToTuple(self, drl):
        """Return a single tuple of relevant results ed.
        """
        return (drl.name, drl.status,
                len(drl),
                NTvalue(drl.rmsdAv, drl.rmsdSd, fmt='%.4f +/ %.4f'), drl.violCount1, drl.violCount3, drl.violCount5, str(drl.rogScore)
               )
    #end def

    def save(self, path):
        """Save CingSummary object as XML file.
        Return True on error
        """
        result = obj2XML( self, path=path )
        if result == None:
            NTerror('CingSummary.save: saving to "%s"', path)
            return True
        #end if
    #end def

    def restore( path ): #@NoSelf
        """
        Static method to restore CingSummary object from XML-file path.
        Return None on error.
        """
        if not os.path.exists( path ):
            NTerror('CingSummary.restore: path "%s" does not exist', path)
            return True
        #end if
        return XML2obj(path = path)
    #end def
#end class

class XMLCingSummaryHandler( XMLhandler ):
    """CingSummary handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='CingSummary')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs == None: return None
        result = CingSummary()
        result.update(attrs)
        return result
    #end def
#end class

# Initiate an instance
xmlcingsummarydicthandler = XMLCingSummaryHandler()