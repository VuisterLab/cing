import cing
import cing.Libs.disk
import cing.core.classes as classes
import cing.core.molecule
import cing.core.pid as pid
import cing.core.validation as validation
import cing.Libs.jsonTools as jsonTools
#import cing.core.jsonHandlers as jsonHandlers
import cing.Libs.io as io
import cing.Libs.NTutils as ntu
import cing.Libs.Adict as adict
from cing.Libs import disk

# set indent=4 as default
cing.Libs.jsonTools.set_encoder_options('json',indent=4)


class AdictJsonHandler(cing.Libs.jsonTools.handlers.AnyDictHandler):
    """Handler for the Adict class
    """
    cls = adict.Adict
#end class
AdictJsonHandler.handles(adict.Adict)


class NTdictJsonHandler(cing.Libs.jsonTools.handlers.AnyDictHandler):
    """Handler for the NTdict class
    """
    cls = ntu.NTdict
#end class
NTdictJsonHandler.handles(ntu.NTdict)


class NTlistJsonHandler(cing.Libs.jsonTools.handlers.AnyListHandler):
    """Handler for the NTlist class
    """
    cls = ntu.NTlist
#end class
NTlistJsonHandler.handles(ntu.NTlist)


class NTvalueJsonHandler(cing.Libs.jsonTools.handlers.AnyDictHandler):
    """Handler for the NTvalue class
    """
    cls = ntu.NTvalue
    def flatten(self, obj, data):
        #cing.Libs.jsonTools.handlers.setVersion(data)
        data['value'] = obj['value']
        return self._flatten(obj, data)

    def restore(self, data):
        a = ntu.NTvalue(value=data['value'])
        return self._restore(data, a)
#end class
NTvalueJsonHandler.handles(ntu.NTvalue)


class NTtreeJsonHandler(cing.Libs.jsonTools.handlers.AnyDictHandler):
    """Handler for the NTvalue class
    """
    cls = ntu.NTtree
    def flatten(self, obj, data):
        #cing.Libs.jsonTools.handlers.setVersion(data)
        data['name'] = obj['name']
        return self._flatten(obj, data)

    def restore(self, data):
        reference = self.context.referenceObject
        tree = ntu.NTtree(name=data['name'])
        self._restore(data, tree)
        for child in tree._children:
            if isinstance(child, pid.Pid) and \
               reference is not None and \
               isinstance(reference, classes.Project):
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


class TimeJsonHandler(cing.Libs.jsonTools.handlers.BaseHandler):
    """Json handler for the Time class
    """
    def flatten(self, obj, data):
        #cing.Libs.jsonTools.handlers.setVersion(data)
        data['time'] = float.__repr__(obj)
        return data

    def restore(self, data):
        #print 'restore>', obj
        return io.Time(data['time'])
#end class
TimeJsonHandler.handles(io.Time)


class ProjectJsonHandler(cing.Libs.jsonTools.handlers.AnyDictHandler):
    """Json handler for the Project class
    """
    def flatten(self, obj, data):
        # have name, version and convention readily available for decoding later as all keys will be 'encoded' in a list
        #cing.Libs.jsonTools.handlers.setVersion(data)
        data['name'] = obj.name
        data['convention'] = cing.constants.INTERNAL
        flatten = self.context.flatten
        data['py/items'] = [flatten([k,obj[k]],reset=False) for k in obj.saveKeys ]
        return data

    def restore(self, data):
        #print 'restore>', data
        p = classes.Project(name=data['name'])
        #print data['items']
        return self._restore(data, p)
#end class
ProjectJsonHandler.handles(classes.Project)


class HistoryJsonHandler(cing.Libs.jsonTools.handlers.AnyListHandler):
    """Handler for the History class
    """
    cls = classes.History
#end class
HistoryJsonHandler.handles(classes.History)


class StatusDictJsonHandler(cing.Libs.jsonTools.handlers.AnyDictHandler):
    """Handler for the StatusDict class
    """
    def flatten(self, obj, data):
        #cing.Libs.jsonTools.handlers.setVersion(data)
        data['key'] = obj['key']
        return self._flatten(obj, data)

    def restore(self, data):
        a = classes.StatusDict(data['key'])
        return self._restore(data, a)
#end class
StatusDictJsonHandler.handles(classes.StatusDict)


class PathJsonHandler(cing.Libs.jsonTools.handlers.BaseHandler):
    """Json handler for the Path class
    """
    def flatten(self, obj, data):
        data['path'] = str(obj)
        return data

    def restore(self, data):
        p = disk.Path(data['path'])
        return p
#end class
PathJsonHandler.handles(disk.Path)


class PidJsonHandler(cing.Libs.jsonTools.handlers.BaseHandler):
    """Json handler for the Pid class
    """
    def flatten(self, obj, data):
        #cing.Libs.jsonTools.handlers.setVersion(data)
        data['pid'] = str(obj)
        return data

    def restore(self, data):
        #print 'restore>', obj
        p = pid.Pid(data['pid'])
        if self.context.metaData is not None and \
           'version' in (self.context.metaData):
            print('PidJsonHandler.restore>> version=', self.context.metaData['version'])
            p._version = self.context.metaData['version']  # restore version info used to create it
        return p
#end class
PidJsonHandler.handles(pid.Pid)


class ObjectPidJsonHandler(cing.Libs.jsonTools.handlers.BaseHandler):
    """Json handler for the Molecule, Chain, Residue, Atom classes
    """
    def flatten(self, obj, data):
        #cing.Libs.jsonTools.handlers.setVersion(data)
        data['pid'] = str(obj.asPid())
        return data

    def restore(self, data):
        return pid.Pid(data['pid'])
#end class
ObjectPidJsonHandler.handles(cing.core.molecule.Molecule)
ObjectPidJsonHandler.handles(cing.core.molecule.Chain)
ObjectPidJsonHandler.handles(cing.core.molecule.Residue)
ObjectPidJsonHandler.handles(cing.core.molecule.Atom)

class ValidationResultsContainerJsonHandler(cing.Libs.jsonTools.handlers.AnyDictHandler):
    """Handler for the ValidationResultsContainer class
    """
    cls = validation.ValidationResultsContainer
    # def flatten(self, obj, data):
    #     data['py/version'] = cing.definitions.cingDefinitions.version
    #     return self._flatten(obj, data)
    #
    # def restore(self, data):
    #     a = validation.ValidationResultsContainer()
    #     return self._restore(data, a)
#end class
ValidationResultsContainerJsonHandler.handles(validation.ValidationResultsContainer)
