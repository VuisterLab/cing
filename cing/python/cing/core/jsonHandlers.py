import cing
import cing.core.molecule
import cing.core.pid as pid
import cing.core.validation as validation

from cing.Libs import jsonTools

import cing.Libs.io as io
import cing.Libs.NTutils as ntu
import cing.Libs.Adict as adict

from cing.Libs import disk
from cing.core import project

# set indent=4 as default
jsonTools.set_encoder_options('json',indent=4)


class AdictJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the Adict class
    """
    namespace = cing.constants.CING_KEY
    cls = adict.Adict
#end class
AdictJsonHandler.handles(adict.Adict)


class NTdictJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the NTdict class
    """
    namespace = cing.constants.CING_KEY
    cls = ntu.NTdict
#end class
NTdictJsonHandler.handles(ntu.NTdict)


class NTlistJsonHandler(jsonTools.handlers.AnyListHandler):
    """Handler for the NTlist class
    """
    namespace = cing.constants.CING_KEY
    cls = ntu.NTlist
#end class
NTlistJsonHandler.handles(ntu.NTlist)


class NTvalueJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the NTvalue class
    """
    namespace = cing.constants.CING_KEY
    cls = ntu.NTvalue

    def flatten(self, obj, data):
        data['value'] = obj['value']
        return self._flatten(obj, data)

    def restore(self, data):
        a = ntu.NTvalue(value=data['value'])
        return self._restore(data, a)
#end class
NTvalueJsonHandler.handles(ntu.NTvalue)


class NTtreeJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the NTtree class
    """
    cls = ntu.NTtree
    namespace = cing.constants.CING_KEY

    def flatten(self, obj, data):
        data['name'] = obj['name']
        return self._flatten(obj, data)

    def restore(self, data):
        reference = self.context.referenceObject
        tree = ntu.NTtree(name=data['name'])
        self._restore(data, tree)
        for child in tree._children:
            if isinstance(child, pid.Pid) and \
               reference is not None and \
               isinstance(reference, project.Project):
                childObj = pid.decodePid(reference, child)
            else:
                childObj = child
            #end if
            if childObj is not None:
                #establish backward and forward linkages
                tree[child.name] = childObj
                childObj._parent = tree
            #end if
        #end for
        return tree
    #end def
#end class
NTtreeJsonHandler.handles(ntu.NTtree)


class TimeJsonHandler(jsonTools.handlers.BaseHandler):
    """Json handler for the Time class
    """
    namespace = cing.constants.CING_KEY

    def flatten(self, obj, data):
        data['time'] = float.__repr__(obj)
        return data

    def restore(self, data):
        #print 'restore>', obj
        return io.Time(data['time'])
#end class
TimeJsonHandler.handles(io.Time)


class ProjectJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Json handler for the Project class
    """
    namespace = cing.constants.CING_KEY

    def flatten(self, obj, data):
        # have name, version and convention readily available for decoding later as all keys will be 'encoded' in a list
        data['name'] = obj.name
        data['convention'] = cing.constants.INTERNAL
        flatten = self.context.flatten
        data['py/items'] = [flatten([k,obj[k]],reset=False) for k in obj.saveKeys ]
        return data

    def restore(self, data):
        p = project.Project(name=data['name'])
        return self._restore(data, p)
#end class
ProjectJsonHandler.handles(project.Project)


class HistoryJsonHandler(jsonTools.handlers.AnyListHandler):
    """Handler for the History class
    """
    namespace = cing.constants.CING_KEY
    cls = project.History
#end class
HistoryJsonHandler.handles(project.History)


class StatusDictJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the StatusDict class
    """
    namespace = cing.constants.CING_KEY

    def flatten(self, obj, data):
        data['key'] = obj['key']
        return self._flatten(obj, data)

    def restore(self, data):
        a = project.StatusDict(data['key'])
        return self._restore(data, a)
#end class
StatusDictJsonHandler.handles(project.StatusDict)


class PathJsonHandler(jsonTools.handlers.BaseHandler):
    """Json handler for the Path class
    """
    namespace = cing.constants.CING_KEY

    def flatten(self, obj, data):
        data['path'] = str(obj)
        return data

    def restore(self, data):
        p = disk.Path(data['path'])
        return p
#end class
PathJsonHandler.handles(disk.Path)


class PidJsonHandler(jsonTools.handlers.BaseHandler):
    """Json handler for the Pid class
    """
    namespace = cing.constants.CING_KEY

    def flatten(self, obj, data):
        data['pid'] = str(obj)
        return data

    def restore(self, data):
        p = pid.Pid(data['pid'])
        if self.context.metadata is not None and \
           'version' in (self.context.metadata):
            #print('PidJsonHandler.restore>> version=', self.context.metadata['version'])
            p._version = self.context.metadata['version']  # restore version info used to create it
        return p
#end class
PidJsonHandler.handles(pid.Pid)


class ObjectPidJsonHandler(jsonTools.handlers.BaseHandler):
    """Json handler for the Molecule, Chain, Residue, Atom classes
    """
    namespace = cing.constants.CING_KEY

    def flatten(self, obj, data):
        data['pid'] = str(obj.asPid())
        return data

    def restore(self, data):
        return pid.Pid(data['pid'])
#end class
ObjectPidJsonHandler.handles(cing.core.molecule.Molecule)
ObjectPidJsonHandler.handles(cing.core.molecule.Chain)
ObjectPidJsonHandler.handles(cing.core.molecule.Residue)
ObjectPidJsonHandler.handles(cing.core.molecule.Atom)

class ValidationResultsContainerJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the ValidationResultsContainer class
    """
    cls = validation.ValidationResultsContainer
    namespace = cing.constants.CING_KEY

    # def flatten(self, obj, data):
    #     data['py/version'] = cing.definitions.cingDefinitions.version
    #     return self._flatten(obj, data)
    #
    # def restore(self, data):
    #     a = validation.ValidationResultsContainer()
    #     return self._restore(data, a)
#end class
ValidationResultsContainerJsonHandler.handles(validation.ValidationResultsContainer)
