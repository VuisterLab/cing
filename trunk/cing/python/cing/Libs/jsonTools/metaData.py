from cing.Libs.jsonTools.handlers import BaseHandler
from cing.Libs.jsonTools import tags

__author__ = 'geerten'

### Separate files because of cyclic imports otherwise??
#GWV
class MetaData(dict):
    """
    just a container to be able to define a handler
    """
#end class

class MetaDataJsonHandler(BaseHandler):
    """
    Handler for the MetaData;
    on decode add a instances as attribute of context for
    subsequent usage
    """
    def flatten(self, obj, data):
        flatten = self.context.flatten
        for k,v in obj.items():
            data[k] = flatten(v,reset=False)
        return data

    def restore(self, data):
        data.pop(tags.OBJECT)
        restore = self.context.restore
        mdata = MetaData()
        for k in data.keys():
            mdata[k] = restore(data[k])
        #end for
        # add to context
        setattr(self.context,'metaData', mdata)
        return mdata
    #end def
#end class
MetaDataJsonHandler.handles(MetaData)
