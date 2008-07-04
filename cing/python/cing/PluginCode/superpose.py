"""
superpose.py

Adds superpose() method to Project class (works on current molecule)

"""

def superpose( project, ranges=None, backboneOnly=True, includeProtons = False, iterations=2  ):
    """
    Calculate a superposition of current active molecule
    return rmsd result of molecule, or None on error

    """

    if not project.molecule:
        NTerror('Project.superpose: undefined molecule')
        return None
    #end if

    if project.molecule.modelCount == 0:
        NTerror('Project.superpose: no coordinates for %s\n', project.molecule)
        return None
    #end if
    project.molecule.superpose(ranges=ranges, backboneOnly=backboneOnly,
                               includeProtons = includeProtons, iterations=iterations
                              )
    return project.molecule.rmsd
#end def

# register the functions
methods  = [(superpose,None)
           ]
#saves    = []
#restores = []
#exports  = []

#print '>>at the end'


