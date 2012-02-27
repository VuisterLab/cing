from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.core.classes import Project
from shutil import rmtree

def run():
    nTdebug("Remove previous project if present")
    pdir = n+".cing"
    if os.path.exists(pdir):
        rmtree(pdir)
    nTdebug("Load project from .tgz")
    project = Project.open(n, status='old')
    if not project:
        sys.exit(1)
    nTdebug("Set convenience variables")
    m = project.molecule
    m.rangesByCv()
# end def

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    n = '1brv'
    run()
# end if
    
