"""
v3: key validation classes and functions, separate from validate which contains the
v1 stuff

        <obj> <-> <validationResultContainer> -> <ValidationResult> -> <obj>
keys: validation   object               'userKeys'               object


validation.getResult, validation.setResult and validation.hasResult are convenience methods

validation.data is a ValidationData instance that contains all the containers.
validation.save is a convenience method to save validation.data
validation.restore is a convenience method to restore validation.data


"""
import sys

from cing import constants
from cing.Libs import Adict
from cing.Libs import io
import cing.core.pid as pid
import cing.Libs.jsonTools as jsonTools

class ValidationData(Adict.Adict):
    """
    Class to store the ValidationResults container instances
    Used for saving/restoring/writing.
    Contains [object.asPid().str, container) key, value pairs
    """
    def add(self, theObject, container):
        """
        Add the container under the object key
        """
        self[theObject.asPid().str] = container
    #end def

    def save(self, toPath):
        """
        Save validation toPath using json encoder
        return True on error
        """
        jsonTools.obj2json(self, toPath)
        return False
    #end def

    def restore(self, fromPath, project=None):
        """
        restore validation data fromPath; establish linkage to project if project is not None
        """
        pass
    #end def

    def write(self, stream=sys.stdout):
        for container in self.itervalues():
            if len(container) > 0:
                stream.write(container.format())
        #end for
    #end def
#end class
data = ValidationData()


class ValidationResultsContainer(Adict.Adict):
    """v3: Container class for validation results
    object is stored under attrOnly constants.OBJECT_KEY
    """
    KEY = 'validation'

    def __init__(self, *args, **kwds):
        Adict.Adict.__init__(self, *args, **kwds)
        self.setattrOnly(constants.OBJECT_KEY, None)
    #end def

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

    def format(self):
        l = 80
        obj = self.getattrOnly(constants.OBJECT_KEY)

        result =  '\n# ' + '='*(l-2) + '\n'
        result += '# %s\n' % obj
        result += '# ' + '='*(l-2) + '\n\n'

        for key, value in self.iteritems():
            if value is not None:
                result += '# ' + '-'*(l-2) + '\n'
                result += '# %s\n' % key
                result += '# ' + '-'*(l-2) + '\n'
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

    def __init__(self):
        Adict.Adict.__init__(self)
        self._pid = pid.Pid.new(self.__class__.__name__, self.getOid()).str
        self[self.OBJECT_KEY] = None

    def __str__(self):
        return '<%s>' % self._pid

    def asPid(self):
        return pid.Pid(self._pid)
    #end def
#end class


def hasValidationResult(theObject,key):
    return getValidationResult(theObject, key) is not None


def getValidationResult(theObject, key, default=None):
    """v3:Returns validation result from theObject for key,
    None if not present or value set to None,
    unless default is defined which is then set and returned
    (in the spirit of dict.setdefault())
    """
    #io.debug('>get> {0!s} {1!s} {2!s}\n', theObject, key, default)
    if theObject is None:
        io.error('getValidationResult: invalid object\n')
        return None
    if key is None:
        io.error('getValidationResult: invalid key\n')
        return None
    #v3: use attribute method so v3 will not 'suffer'
    if not hasattr(theObject, ValidationResultsContainer.KEY):
        if default is not None:
            setValidationResult(theObject, key, default)
        return default # ==None or default
    #end if
    container = getattr(theObject, ValidationResultsContainer.KEY)
    if key not in container:
        if default is not None:
            setValidationResult(theObject, key, default)
        return default # ==None or default
    #endif
    result = container[key]
    if result is None and default is not None:
        setValidationResult(theObject, key, default)
        return default # ==None or default
    return result # ==result
#end def


def setValidationResult(theObject, key, result):
    """v3: Add result to theObject's validation container instance under key,
    add reverse linkage to result under constants.OBJECT_KEY
    return True on error
    """
    #io.debug('>set> {0!s} {1!s} {2!s}\n', theObject, key, result)
    if theObject is None:
        io.error('setValidationResult: invalid object\n')
        return True
    if key is None:
        io.error('setValidationResult: invalid key\n')
        return True
    #v3: use attribute method so v3 will not 'suffer'
    # check if theObject has a validation container, create one if needed
    if not hasattr(theObject, ValidationResultsContainer.KEY):
        container = ValidationResultsContainer()
        setattr(theObject, ValidationResultsContainer.KEY, container)
        container.setattrOnly(constants.OBJECT_KEY, theObject)
    else:
        container = getattr(theObject, ValidationResultsContainer.KEY)
    #end if

    # add this container to the data
    data.add(theObject, container)

    # add the result and set the object's reference
    container[key] = result
    if result is not None:
        result[constants.OBJECT_KEY] = theObject
        if hasattr(theObject,'asPid'):
            result._pid = pid.Pid.new(result.__class__.__name__,
                                      theObject.asPid().id,
                                      ValidationResultsContainer.KEY,
                                      key
                                     )
        #end if
    #end if
    return False
#end def

# convenience
getResult = getValidationResult
setResult = setValidationResult
hasResult = hasValidationResult

save = data.save
restore = data.restore
write = data.write