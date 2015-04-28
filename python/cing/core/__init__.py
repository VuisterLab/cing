"""
-------------------------------------------------------------------------------
CING Package Contents:
-------------------------------------------------------------------------------
classes        Project, Restraints, Lists and auxiliary classes.
constants      CING constants, definitions and parameters.
database       CING database implementation.
importPlugin   CING plugin implementation
molecule       Molecule, Chain, Residue, Atom, Coordinate, Ensemble and Model
               classes.
parameters     CING non-user parameters.
sml            CING internal storage ('Simple Markup Language') implementation.
test           Testing routines.

-------------------------------------------------------------------------------
CING API layout:
-------------------------------------------------------------------------------

                           [Coordinate0_of_atom0, Coordinate0_of_atom1, ...]
                              ^
                              |
             Ensemble <-> [Model0, Model1, ...]
                ^                     |
                |                     v
                |             [Coordinate1_of_atom0, Coordinate1_of_atom1, ...]
                |
                |
                |
                |         NTdb <-> ResidueDef <-> AtomDef
                |                      ^          ^
                |                      |          |
                v                      v          v
  Project ->  Molecule <-> Chain <-> Residue <-> Atom <-> Resonance <- Peak
     ^          ^           ^          ^          ^   <-> Coordinate
     |          |           |          |          |
-------------------------------------------------------------------------------
CCPN API linkage:
-------------------------------------------------------------------------------
     |          |           |          |          |
     v          v           |          v          v
 ccpnProject ccpnMolecule   v      ccpnResidue ccpnAtom
                          ccpnChain


  Project.ccpn     = ccpnProject    (Molecule.ccpn      =  ccpnMolecule and so on)
  ccpnProject.cing = Project        (ccpnMolecule.cing  =  Molecule and so on)

  ccpnProject :: (memops.Implementation.Project)
  ccpnMolecule = ccpnProject.molSystems[0]   :: (ccp.molecule.MolSystem.MolSystem)
  ccpnChain   in ccpnMolecule.sortedChains() :: (ccp.molecule.MolSystem.Chain)
  ccpnResidue in ccpnChain.sortedResidues()  :: (ccp.molecule.MolSystem.Residue)
  ccpnAtom    in ccpnResidue.sortedAtoms()   :: (ccp.molecule.MolSystem.Atom)

-------------------------------------------------------------------------------
Mapping between the CING data model, NMR-STAR and CCPN:
-------------------------------------------------------------------------------

  CING     | NMR-STAR             CCPN
  --------------------------------
  Molecule | Molecular system     MolSystem (from ccp.api.molecule.MolSystem)
  Chain    | Assembly entity      Chain
  Residue  | Chemical component   Residue

There are things that will be difficult to map from one to the other.
A Zinc ion will usually be part of the same chain in CING whereas it will be
in a different assembly entity in NMR-STAR. This has consequences for numbering.
-------------------------------------------------------------------------------
"""
import cing

__version__         = cing.__version__
__revision__        = cing.__revision__
__date__            = cing.__date__
__author__          = cing.__author__
__copyright__       = cing.__copyright__
__copyright_years__ = cing.__copyright_years__
__credits__         = cing.__credits__

