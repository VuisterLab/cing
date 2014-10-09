import cing
import cing.Libs.jsonTools as jsonTools
import cing.Libs.io as io
import cing.Libs.NTutils as ntu
import cing.Libs.Adict as adict


class AdictJsonHandler(jsonTools.handlers.AnyDictHandler):
    """Handler for the Adict class
    """
    def flatten(self, obj, data):
        data['version'] = cing.definitions.cingDefinitions.version
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
        data['version'] = cing.definitions.cingDefinitions.version
        return self._flatten(obj, data)

    def restore(self, data):
        d = ntu.NTdict()
        return self._restore(data, d)
#end class
NTdictJsonHandler.handles(ntu.NTdict)


class NTlistJsonHandler(jsonTools.handlers.AnyListHandler):
    """Handler for the NTlist class
    """
    def flatten(self, obj, data):
        data['version'] = cing.definitions.cingDefinitions.version
        return self._flatten(obj, data)

    def restore(self, data):
        #print "restore>", obj
        a = ntu.NTlist()
        return self._restore(data, a)
#end class
NTlistJsonHandler.handles(ntu.NTlist)


class TimeJsonHandler(jsonTools.handlers.BaseHandler):
    """Json handler for the Time class
    """
    def flatten(self, obj, data):
        data['version'] = cing.definitions.cingDefinitions.version
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
        data['version'] = cing.definitions.cingDefinitions.version
        data['convention'] = cing.constants.INTERNAL
        flatten = self.context.flatten
        data['items'] = [flatten([k,obj[k]],reset=False) for k in obj.saveKeys ]
        return data

    def restore(self, data):
        #print 'restore>', data
        p = cing.Project(name=data['name'])
        #print data['items']
        return self._restore(data, p)
#end class
ProjectJsonHandler.handles(cing.Project)

class HistoryJsonHandler(jsonTools.handlers.AnyListHandler):
    """Handler for the History class
    """
    def flatten(self, obj, data):
        data['version'] = cing.definitions.cingDefinitions.version
        return self._flatten(obj,data)

    def restore(self, data):
        h = cing.core.classes.History()
        return self._restore(data, h)
#end class
HistoryJsonHandler.handles(cing.core.classes.History)