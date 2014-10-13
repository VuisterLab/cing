"""
V3 Code to put Project related classes
Just a stub for now
"""

__author__ = 'geerten'

#stub
from cing.core.classes import Project
from cing.core.classes import History
from cing.core.classes import StatusDict

from cing.core.constants import PROJECT_OLD
from cing.core.constants import PROJECT_CREATE
from cing.core.constants import PROJECT_NEW
from cing.core.constants import PROJECT_NEWFROMCCPN
from cing.core.constants import PROJECT_OLDFROMCCPN


# convenience methods
open = Project.open

def create(name, restore=True):
    return Project.open(name, status=PROJECT_CREATE, restore=restore)

def new(name, restore=False):
    return Project.open(name, status=PROJECT_NEW, restore=restore)

def newFromCcpn(name, restore=False):
    return Project.open(name, status=PROJECT_NEWFROMCCPN, restore=restore)

def oldFromCcpn(name, restore=True):
    return Project.open(name, status=PROJECT_OLDFROMCCPN, restore=restore)

