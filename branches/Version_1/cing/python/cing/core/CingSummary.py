from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqProcheck import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing import plugins
from cing.Libs.fpconst import NaN


# pylint: disable=R0902
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

                         # rmsd's
                         rmsdToMean_backboneAverage   = None,
                         rmsdToMean_heavyAtomsAverage = None,
                         ranges                       = None,

                         # CING scores in %
                         cing_red            = NaN,
                         cing_orange         = NaN,
                         cing_green          = NaN,
                         CING_residueROG     = NTlist(),

                         # Procheck scores
                         pc_core            = NaN,
                         pc_allowed         = NaN,
                         pc_generous        = NaN,
                         pc_disallowed      = NaN,
                         pc_gf              = None,

                         # WHATIF scores done again later; just here to make sure for the format statement
                         WI_ramachandran    = None,
                         WI_bbNormality     = None,
                         WI_janin           = None,

                         distances          = NTlist(),
                         dihedrals          = NTlist(),
                         rdcs               = NTlist(),

                        # single line format
                         __FORMAT__ = \
          '%(name)-10s   ' +\
          'RESIDUES: tot %(totalResidueCount)3d  prot %(proteinResidueCount)3d  nucl %(nucleicResidueCount)3d   ' +\
          'ROG(%%): %(cing_red)5.1f %(cing_orange)5.1f %(cing_green)5.1f    ' +\
          'PROCHECK(%%): %(pc_core)5.1f %(pc_allowed)5.1f %(pc_generous)5.1f %(pc_disallowed)5.1f  gf: %(pc_gf)-15s  ' +\
          'WHATIF: rama %(WI_ramachandran)-15s bb %(WI_bbNormality)-15s janin %(WI_janin)-15s '
                    )
        if getDeepByKeysOrAttributes( plugins, WHATIF_STR, IS_INSTALLED_STR):
#            from cing.PluginCode.Whatif import Whatif # JFD: This breaks the plugin concept somewhat.
            # Add all Whatif summary check Id's
            # The below causes an exception when called on a system that has no Whatif.
            for checkId in summaryCheckIdList:
                key = 'WI_' + cingCheckId(checkId)
                self[key] = None
        #end if

        self.saveAllXML()
    #end def

    def getSummaryFromProject( self, project ):
        """
        Extract the data from project
        """

        self.name = project.name
        if project.molecule == None:
            nTwarning("No molecule found in project in getSummaryFromProject")
            return self

        # Residue counts (total, protein, nucleic)
        self.totalResidueCount   = len( project.molecule.allResidues() )
        proteinResidues = project.molecule.residuesWithProperties('protein' )
        self.proteinResidueCount = len( proteinResidues )
        nucleicResidues = project.molecule.residuesWithProperties('nucleic' )
        self.nucleicResidueCount = len( nucleicResidues )

        # rmsds
        if project.molecule and project.molecule.has_key('rmsd'):
            rmsdObject = project.molecule.rmsd
            if rmsdObject == None:
                self.rmsdToMean_backboneAverage = NaN
                self.rmsdToMean_heavyAtomsAverage = NaN
                self.ranges = None
            else:
                self.rmsdToMean_backboneAverage = getDeepByKeysOrAttributes(rmsdObject,BACKBONE_AVERAGE_STR)
                self.rmsdToMean_heavyAtomsAverage = getDeepByKeysOrAttributes(rmsdObject,HEAVY_ATOM_AVERAGE_STR)
                self.ranges = project.molecule.residueList2Ranges(rmsdObject.ranges)
        #end if

        # ROG scores
        rog = NTlist( 0, 0, 0 ) # Counts for red, orange, green.
        for residue in project.molecule.allResidues():
            if residue.rogScore.isRed():
                rog[0] += 1
            elif residue.rogScore.isOrange():
                rog[1] += 1
            else:
                rog[2] += 1
            self.CING_residueROG.append( (residue.cName(-1), residue.rogScore) )
        #end for
        total = reduce(lambda x, y: x+y+0.0, rog) # total expressed as a float because of 0.0
        for i, _x in enumerate(rog):
            rog[i] = rog[i]*100.0/total
        self.cing_red    = round(rog[0],1)
        self.cing_orange = round(rog[1],1)
        self.cing_green  = round(rog[2],1)

        # Procheck (core, allowed,  generous, disallowed) (%), average g_factor
        pcSummary = getDeepByKeysOrAttributes(project.molecule, PROCHECK_STR, SUMMARY_STR)
        if (self.proteinResidueCount > 0 and pcSummary):
#            nTdebug("Going to add procheck results to summary.")
#            nTmessage("E.g.: project.molecule.procheck.summary.core: [%8.3f]" % project.molecule.procheck.summary.core)
            self.pc_core       = pcSummary.core
            self.pc_allowed    = pcSummary.allowed
            self.pc_generous   = pcSummary.generous
            self.pc_disallowed = pcSummary.disallowed
            self.pc_gf  = proteinResidues.zap('procheck','gf').average2(fmt='%6.3f +/- %5.3f')
#        else:
#            nTmessage("Skipping adding procheck results since no results available or no protein residues or...")
        #end if

        # Whatif
# GWV disabled check
#       if hasattr(plugins, WHATIF_STR) and plugins[ WHATIF_STR ].isInstalled:
        if (self.proteinResidueCount > 0 and
            project.whatifStatus.completed and project.whatifStatus.parsed and
            project.molecule.has_key(WHATIF_STR)
           ):
            for checkId in summaryCheckIdList:
                if project.molecule[WHATIF_STR].has_key(checkId):
                    key = 'WI_' + cingCheckId(checkId)
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
                len(drl), len(drl.intraResidual), len(drl.sequential),len(drl.mediumRange),len(drl.longRange),len(drl.ambiguous),
                NTvalue(drl.rmsdAv, drl.rmsdSd, fmt='%.4f +/ %.4f'), drl.violCountLower,
                drl.violCount1, drl.violCount3, drl.violCount5, str(drl.rogScore)
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
            nTerror('CingSummary.save: saving to "%s"', path)
            return True
        #end if
    #end def

    def restore( path ): #@NoSelf # pylint: disable=E0213
        """
        Static method to restore CingSummary object from XML-file path.
        Return None on error.
        """
        if not os.path.exists( path ):
            nTerror('CingSummary.restore: path "%s" does not exist', path)
            return True
        #end if
        return xML2obj(path = path)
    #end def
#end class

class XMLCingSummaryHandler( XMLhandler ):
    """CingSummary handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='CingSummary')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs == None:
            return None
        result = CingSummary()
        result.update(attrs)
        return result
    #end def
#end class


# Initiate an instance
xmlcingsummarydicthandler = XMLCingSummaryHandler()