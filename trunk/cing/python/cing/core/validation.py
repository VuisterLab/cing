"""
v3: key validation classes and functions, separate from validate which contains the
v1 stuff

        <obj> <-> <validationResultContainer> -> <ValidationResult> -> <obj>
keys: validation   object               'userKeys'               object



"""
import sys

from cing import constants
from cing.Libs import Adict
from cing.Libs import io
import cing.constants.definitions as cdefs
import cing.core.pid as pid
import cing.Libs.jsonTools as jsonTools


class ValidationData(Adict.Adict):
    """
    Class to store the ValidationResults container instances
    Used for saving/restoring/writing.
    Contains [object.asPid.str, container) key, value pairs
    """
    PROJECT = 'project'
    #STATUS  = 'status'
    DATA    = 'data'

    def __init__(self, theProject):
        Adict.Adict.__init__(self)
        self.project = theProject
        self.data    = {}
    #end def

    def addContainer(self, theObject, container):
        """
        Add the container under the object key
        """
        setattr(theObject, ValidationResultsContainer.KEY, container)
        container.setattrOnly(constants.OBJECT_KEY, theObject)
        self.data[theObject.asPid.str] = container
    #end def

    def save(self, toPath=None):
        """
        Save validation toPath using json encoder
        return True on error
        """
        if toPath is None:
            toPath = self.project.path() / cdefs.directories.validation / cdefs.cingPaths.validation

        jsonTools.obj2json(self.data, toPath)
        return False
    #end def

    def restore(self, fromPath=None, restoreLinkages=True):
        """
        restore validation data fromPath (set to default if None);
        establish linkage to project if restoreLinkages == True

        return True on error
        """
        if fromPath is None:
            fromPath = self.project.path() / cdefs.directories.validation / cdefs.cingPaths.validation
        if restoreLinkages:
            vdata, metadeta = jsonTools.json2obj(fromPath, self.project)
        else:
            vdata, metadeta = jsonTools.json2obj(fromPath)

        if vdata is None: return True

        # update the data containers
        for pid, container in vdata.iteritems():
            if pid in self.data:
                # we already have a container for this object => update the container elements
                self.data[pid].update(container)
            else:
                # we don't have it yet, just add
                self.data[pid] = container
                if restoreLinkages:
                    obj = self.project.getByPid(pid)
                    if obj is None:
                        io.error('ValidationData.restore: unable to decode "{0}\n', pid)
                    else:
                        self.addContainer(obj, container)
                    #end if
                #end if
            #end if
        #end for
    #end def

    def clear(self, project=None):
        """
        clear the data; remove from project if project is not None
        """
        for pid,container in self.data.iteritems():
            if project is not None:
                obj = project.getByPid(pid)
                if obj is not None:
                    del obj[ValidationResultsContainer.KEY]
            #end if
            del self.data[pid]
        #end for
    #end def

    def write(self, stream=sys.stdout):
        for container in self.data.itervalues():
            if len(container) > 0:
                stream.write(container.format())
        #end for
    #end def

    def setResult(self, theObject, key, result):
        """v3: Add result to theObject's validation container instance under key,
        add reverse linkage to result under constants.OBJECT_KEY
        add container to self
        return True on error
        """
        #io.debug('>set> {0!s} {1!s} {2!s}\n', theObject, key, result)
        if theObject is None:
            io.error('ValidationData.setResult: invalid object\n')
            return True
        if key is None:
            io.error('ValidationData.setResult: invalid key\n')
            return True
        #v3: use attribute method so v3 will not 'suffer'
        # check if theObject has a validation container, create one if needed
        if not hasattr(theObject, ValidationResultsContainer.KEY):
            container = ValidationResultsContainer()
            # add this container
            self.addContainer(theObject, container)
            # setattr(theObject, ValidationResultsContainer.KEY, container)
            # container.setattrOnly(constants.OBJECT_KEY, theObject)
        else:
            container = getattr(theObject, ValidationResultsContainer.KEY)
        #end if

        # add the result and set the object's reference
        # conditionally adjust the the pid of result instance
        container[key] = result
        if result is not None:
            result[constants.OBJECT_KEY] = theObject
            if hasattr(theObject,'asPid'):
                result.setPid(theObject.asPid.id,
                              ValidationResultsContainer.KEY,
                              key
                             )
            #end if
        #end if
        return False
    #end def

    def hasResult(self, theObject, key):
        return self.getResult(theObject, key) is not None

    def getResult(self, theObject, key, default=None):
        """v3:Returns validation result from theObject for key,
        None if not present or value set to None,
        unless default is defined which is then set and returned
        (in the spirit of dict.setdefault())
        """
        #io.debug('>get> {0!s} {1!s} {2!s}\n', theObject, key, default)
        if theObject is None:
            io.error('ValidationData.getResult: invalid object\n')
            return None
        if key is None:
            io.error('ValidationData.getResult: invalid key\n')
            return None
        #v3: use attribute method so v3 will not 'suffer'
        if not hasattr(theObject, ValidationResultsContainer.KEY):
            if default is not None:
                self.setResult(theObject, key, default)
            return default # ==None or default
        #end if
        container = getattr(theObject, ValidationResultsContainer.KEY)
        if key not in container:
            if default is not None:
                self.setResult(theObject, key, default)
            return default # ==None or default
        #endif
        result = container[key]
        if result is None and default is not None:
            self.setResult(theObject, key, default)
            return default # ==None or default
        return result # ==result
    #end def
#end class


class ValidationResultsContainer(Adict.Adict):
    """v3: Container class for validation results
    object is stored under attrOnly constants.OBJECT_KEY
    """
    KEY = 'validation'

    def __init__(self, *args, **kwds):
        Adict.Adict.__init__(self, *args, **kwds)
        self.setattrOnly(constants.OBJECT_KEY, None)
        # _pid = pid.Pid.new(self.__class__.__name__, self.getOid()).str
        # self.setattrOnly(ValidationResult.PID_KEY, _pid)    #end def

    def __len__(self):
        """
        Return number of non-None elements
        """
        count = 0
        for k,v in self.iteritems():
            if v is not None: count += 1
        #end for
        return count
    #end def

    def __str__(self):
        obj = self.getattrOnly(constants.OBJECT_KEY)
        return '<ValidationResultsContainer: %s, keys: %s>' % (obj, self.keys())

    def format(self):
        l = 80
        obj = self.getattrOnly(constants.OBJECT_KEY)

        result =  '\n#' + '='*(l-2) + '\n'
        result += '# %s\n' % obj
        result += '#' + '='*(l-2) + '\n\n'

        for key, value in self.iteritems():
            if value is not None:
                result += '#' + '-'*(l-2) + '\n'
                result += '# %s\n' % key
                result += '#' + '-'*(l-2) + '\n'
                result += io.formatDictItems(value,
                                             '{key:20} : {value!s}\n'
                                            )
            #end if
        #end for
        return result
    #end def
#end class


class ValidationResult(Adict.Adict):
    """v3:base class for validation results dict's
    """
    OBJECT_KEY = constants.OBJECT_KEY
    PID_KEY = '_pid'

    def __init__(self):
        Adict.Adict.__init__(self)
        # done in Adict now
#        _pid = pid.Pid.new(self.__class__.__name__, self.getOid()).str
#        self.setattrOnly(ValidationResult.PID_KEY, _pid)
        self[self.OBJECT_KEY] = None

    def __str__(self):
        _pid = self.getattrOnly(ValidationResult.PID_KEY)
        return '<%s>' % _pid

    # @property
    # def asPid(self):
    #     _pid = self.getattrOnly(ValidationResult.PID_KEY)
    #     return pid.Pid(_pid)
    # #end def
#end class
