import cing
import cing.Libs.jsonTools as jsonTools
import cing.Libs.io as io
import cing.Libs.NTutils as ntu


class NTdictJsonHandler(jsonTools.handlers.BaseHandler):
    """Handler for the ntdict class
    """
    def flatten(self, obj, data):
        data['version'] = cing.definitions.cingDefinitions.version
        data['convention'] = cing.constants.INTERNAL
        data['items'] = []
        for k in obj.keys():
            data['items'].append( (k,jsonTools.encode(obj[k])) )
        return data

    def restore(self, obj):
        #print "restore>", obj
        a = ntu.NTdict()
        for key,value in obj['items']:
            a[key] = jsonTools.decode(value)
        return a
#end class
jsonTools.handlers.register(ntu.NTdict,NTdictJsonHandler)


class NTlistJsonHandler(jsonTools.handlers.BaseHandler):
    """Handler for the NTlist class
    """
    def flatten(self, obj, data):
        data['version'] = cing.definitions.cingDefinitions.version
        data['convention'] = cing.constants.INTERNAL
        data['values'] = []
        for k in obj:
            data['values'].append( jsonTools.encode(k) )
        return data

    def restore(self, obj):
        #print "restore>", obj
        a = ntu.NTlist()
        for value in obj['values']:
            a.append( jsonTools.decode(value) )
        return a
#end class
jsonTools.handlers.register(ntu.NTlist,NTlistJsonHandler)


class TimeJsonHandler(jsonTools.handlers.BaseHandler):
    """Json handler for the Time class
    """
    def flatten(self, obj, data):
        data['version'] = cing.definitions.cingDefinitions.version
        data['convention'] = cing.constants.INTERNAL
        data['time'] = float.__repr__(obj)
        return data

    def restore(self, obj):
        #print 'restore>', obj
        return io.Time(obj['time'])
#end class
jsonTools.handlers.register(io.Time, TimeJsonHandler)


class ProjectJsonHandler(jsonTools.handlers.BaseHandler):
    """Json handler for the Project class
    """
    def flatten(self, project, data):
        # have name and version readily available for decoding later as all keys will be 'encoded' in a list
        data['name'] = project.name
        data['version'] = cing.definitions.cingDefinitions.version
        data['convention'] = cing.constants.INTERNAL
        data['items'] = [(k,jsonTools.encode(project[k])) for k in project.saveKeys ]
        return data

    def restore(self, data):
        #print 'restore>', data
        p = cing.core.classes.Project(name=data['name'])
        for key,value in data['items']:
            #print '>>', key, value
            p[key] = jsonTools.decode(value)
        return p
#end class
# register this handler
jsonTools.handlers.register(cing.core.classes.Project,ProjectJsonHandler)


class HistoryJsonHandler(jsonTools.handlers.BaseHandler):
    """Handler for the History class
    """
    def flatten(self, obj, data):
        data['version'] = cing.definitions.cingDefinitions.version
        data['convention'] = cing.constants.INTERNAL
        data['values'] = []
        for k in obj:
            data['values'].append( jsonTools.encode(k) )
        return data

    def restore(self, obj):
        #print "restore>", obj
        a = cing.core.classes.History()
        for value in obj['values']:
            a.append( jsonTools.decode(value) )
        return a
#end class
jsonTools.handlers.register(cing.core.classes.History,HistoryJsonHandler)