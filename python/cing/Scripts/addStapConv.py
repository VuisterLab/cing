#!/usr/bin/env python

import cing
import os
import sys
from cing import cingPythonCingDir
from cing.Libs.NTutils import getCallerFileName, nTdebug, nTwarning
from cing.core.database import NTdb
from cing.core.database import saveToSML


def copy_from_convention(from_convention, new_convention, protein_only=True):
    """Copy nomenclature convention from from_convention to new_convention.

    Only copy standard protein residues if protein_only (defaults to True).
    """
    residue_definitions = NTdb.residuesWithProperties('protein')
    if not protein_only:
        residue_definitions = NTdb.allResidueDefs()

    for res_def in residue_definitions:
        nTdebug("Copying %s nomenclature convention to %s for %s",
                from_convention, new_convention, res_def)
        res_def.nameDict[new_convention] = res_def.nameDict[from_convention]
        for atom_def in res_def:
            atom_def.nameDict[new_convention] = atom_def.nameDict[
                from_convention]
            atom_def.postProcess()
        res_def.postProcess()


def correct_hg_stap(res_def):
    """Correct cysteine and serine HG for STAP."""
    nTdebug('Applying %s HG STAP naming conventions', res_def)
    res_def['HG'].nameDict['STAP'] = 'HG1'


def correct_his_stap(mol_def):
    """Correct histidine residue definitions for STAP."""
    nTdebug('Applying histidine STAP naming conventions')
    mol_def['HIS'].nameDict['STAP'] = 'HSD'
    mol_def['HISE'].nameDict['STAP'] = 'HSE'
    mol_def['HISH'].nameDict['STAP'] = 'HSP'


def correct_ile_d_stap(res_def):
    """Correct cysteine delta for STAP."""
    nTdebug('Applying isoleucine CD1/HD123 STAP naming conventions')
    res_def['CD1'].nameDict['STAP'] = 'CD'
    for name, repl in [('HD11', 'HD1'), ('HD12', 'HD2'), ('HD13', 'HD3')]:
        res_def[name].nameDict['STAP'] = repl


def correct_termini_stap(res_def):
    """Change nomenclature conventions for termini to STAP convention.

    For the N-terminal protons HT1/2/3 'H1', 'H2' and 'H3' are added.
    The C-terminal protons are: 'O,OT1' and 'OXT,OT2'.
    """
    nTdebug('Correcting terminal protons to STAP convention for %s', res_def)
    for name, repl in [('H1', 'H1,HT1'), ('H2', 'H2,HT2'), ('H3', 'H3,HT3'),
                       ('O', 'O,OT1'), ('OXT', 'OXT,OT2')]:
        if name in res_def:
            res_def[name].nameDict['STAP'] = repl


def remove_non_stap_residues(res_def):
    """Set name to None for non-stap residue definitions.

    ARGx HH1 is not set to None.
    ASPH HD2 is None.
    GLUH HE2 is not set to None.
    """
    non_stap = ['ARGx', 'ASPH', 'GLUH', 'LYSx']
    for res in non_stap:
        nTdebug('Removing %s from STAP residue definitions', res)
        res_def[res].nameDict['STAP'] = None


def remove_pseudo_atoms(res_def, convention='STAP'):
    """Remove pseudo atoms from this convention in the residue definition.

    Return the corrected res_def.
    """
    nTdebug('Removing STAP pseudo atoms from %s', res_def)
    for pseudo_name in res_def.atomsWithProperties('pseudoatom'):
        nTdebug('Removing %s', pseudo_name)
        res_def[pseudo_name].nameDict['STAP'] = None
    return res_def


def correct_xplor_stap(protein_only=True):
    """Correct atom definitions copied from XPLOR for STAP.

    Only correct standard protein residues if protein_only (defaults to True).
    """
    remove_non_stap_residues(NTdb)
    correct_his_stap(NTdb)
    correct_hg_stap(NTdb['CYS'])
    correct_hg_stap(NTdb['SER'])
    correct_ile_d_stap(NTdb['ILE'])

    residue_definitions = NTdb.residuesWithProperties('protein')
    if not protein_only:
        residue_definitions = NTdb.allResidueDefs()

    for res_def in residue_definitions:
        correct_termini_stap(res_def)
        remove_pseudo_atoms(res_def)


def save_database(db):
    """Resolve the path of the database db and save it to SML."""
    path = os.path.realpath(os.path.join(cingPythonCingDir, 'Database', db))
    saveToSML(NTdb, path, db)


if __name__ == '__main__':
    """Add STAP convention to INTERNAL_1 database.

    Execute as:
        cing --script=addStapConv.py --noProject
    """
    # DEFAULT: 1 disable only when needed.
    if 1:
        nTwarning("Don't execute this script %s by accident. It damages CING." %
                  getCallerFileName())
        sys.exit(1)

    cing.verbosity = cing.verbosityDebug
    copy_from_convention(from_convention='XPLOR', new_convention='STAP')
    correct_xplor_stap()
    save_database(db='INTERNAL_1')
