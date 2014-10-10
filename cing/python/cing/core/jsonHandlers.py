import cing
import cing.core.classes as classes
import cing.core.molecule
import cing.core.pid as pid
import cing.core.validation as validation
import cing.Libs.jsonTools as jsonTools
import cing.Libs.io as io
import cing.Libs.NTutils as ntu
import cing.Libs.Adict as adict


class AnyListHandler(jsonTools.handlers.BaseHandler):
    """
    Base class for list objects
    GWV
    """
    cls = list  # redefine for other classes

    def flatten(self, obj, data):
        """
        Potentially needs subclassing
        """
        return self._flatten(obj,data)

    def _flatten(self, obj, data):
        data['py/version'] = '%s:%s' % (cing.constants.CING_KEY,
                                        cing.definitions.cingDefinitions.version
                                       )
        flatten = self.context.flatten
        data['py/values'] = [flatten(k,reset=False) for k in obj]
        return data

    def restore(self, data):
        """
        Potentially needs subclassing
        """
        obj = self.cls()
        print 'AnyListHandler.restore>', type(obj)
        return self._restore(data, obj)

    def _restore(self, data, obj):
        """
        restores key, values from data into object
        """
        if obj is None: return None
        restore = self.context.restore
        for value in data['py/values']:
            obj.append(restore(value, reset=False))
        return obj
#end class


class AdictJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the Adict class
    """
    def flatten(self, obj, data):
        data['py/version'] = cing.definitions.cingDefinitions.version
        return self._flatten(obj, data)

    def restore(self, data):
        a = adict.Adict()
        return self._restore(data, a)
#end class
AdictJsonHandler.handles(adict.Adict)


class NTdictJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the NTdict class
    """
    def flatten(self, obj, data):
        data['py/version'] = cing.definitions.cingDefinitions.version
        return self._flatten(obj, data)

    def restore(self, data):
        d = ntu.NTdict()
        return self._restore(data, d)
#end class
NTdictJsonHandler.handles(ntu.NTdict)


class NTlistJsonHandler(AnyListHandler):
    """Handler for the NTlist class
    """
    cls = ntu.NTlist
    # def flatten(self, obj, data):
    #     data['py/version'] = cing.definitions.cingDefinitions.version
    #     return self._flatten(obj, data)

    # def restore(self, data):
    #     #print "restore>", obj
    #     a = ntu.NTlist()
    #     return self._restore(data, a)
#end class
NTlistJsonHandler.handles(ntu.NTlist)


class TimeJsonHandler(jsonTools.handlers.BaseHandler):
    """Json handler for the Time class
    """
    def flatten(self, obj, data):
        data['py/version'] = cing.definitions.cingDefinitions.version
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
    def flatten(self, obj, data):
        # have name, version and convention readily available for decoding later as all keys will be 'encoded' in a list
        data['name'] = obj.name
        data['py/version'] = cing.definitions.cingDefinitions.version
        data['convention'] = cing.constants.INTERNAL
        flatten = self.context.flatten
        data['items'] = [flatten([k,obj[k]],reset=False) for k in obj.saveKeys ]
        return data

    def restore(self, data):
        #print 'restore>', data
        p = classes.Project(name=data['name'])
        #print data['items']
        return self._restore(data, p)
#end class
ProjectJsonHandler.handles(classes.Project)


class HistoryJsonHandler(AnyListHandler):
    """Handler for the History class
    """
    cls = classes.History
    # def flatten(self, obj, data):
    #     data['py/version'] = cing.definitions.cingDefinitions.version
    #     return self._flatten(obj,data)
    #
    # def restore(self, data):
    #     h = classes.History()
    #     return self._restore(data, h)
#end class
HistoryJsonHandler.handles(classes.History)


class StatusDictJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the StatusDict class
    """
    def flatten(self, obj, data):
        data['py/version'] = cing.definitions.cingDefinitions.version
        data['key'] = obj['key']
        return self._flatten(obj, data)

    def restore(self, data):
        a = classes.StatusDict(data['key'])
        return self._restore(data, a)
#end class
StatusDictJsonHandler.handles(classes.StatusDict)


class PidJsonHandler(jsonTools.handlers.BaseHandler):
    """Json handler for the Pid class
    """
    def flatten(self, obj, data):
        data['py/version'] = obj._version
        data['pid'] = str(obj)
        return data

    def restore(self, data):
        #print 'restore>', obj
        p = pid.Pid(data['pid'])
        p._version = data['py/version']  # restore version info used to create it
        return p
#end class
PidJsonHandler.handles(pid.Pid)


class ObjectPidJsonHandler(jsonTools.handlers.BaseHandler):
    """Json handler for the Molecule, Chain, Residue, Atom classes
    """
    def flatten(self, obj, data):
        data['py/version'] = cing.definitions.cingDefinitions.version
        data['pid'] = str(obj.asPid())
        return data

    def restore(self, data):
        #print 'restore>', obj
        return pid.Pid(data['pid'])
#end class
ObjectPidJsonHandler.handles(cing.core.molecule.Molecule)
ObjectPidJsonHandler.handles(cing.core.molecule.Chain)
ObjectPidJsonHandler.handles(cing.core.molecule.Residue)
ObjectPidJsonHandler.handles(cing.core.molecule.Atom)

class ValidationResultsContainerJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the ValidationResultsContainer class
    """
    def flatten(self, obj, data):
        data['py/version'] = cing.definitions.cingDefinitions.version
        return self._flatten(obj, data)

    def restore(self, data):
        a = validation.ValidationResultsContainer()
        return self._restore(data, a)
#end class
ValidationResultsContainerJsonHandler.handles(validation.ValidationResultsContainer)
