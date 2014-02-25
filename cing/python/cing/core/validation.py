"""
v3: key validation classes and functions, separate from validate which contains the
v1 stuff

        <obj> <-> <validationResultContainer> -> <ValidationResult> -> <obj>
keys: validation   object               'userKeys'               object
"""

from cing import constants
from cing.Libs import Adict
from cing.Libs import io


class ValidationResultsContainer(Adict.Adict):
    """v3: Container class for validation results
    object is stored under attrOnly constants.OBJECT_KEY
    """
    KEY = 'validation'

    def __init__(self, *args, **kwds):
        Adict.Adict.__init__(self, *args, **kwds)
        self.setattrOnly(constants.OBJECT_KEY, None)
    #end def

    def format(self):
        object = self.getattrOnly(constants.OBJECT_KEY)
        if object == None:
            return ''
        result = '======== %s ========\n' % str(object)
        for key, value in self.iteritems():
            if value is not None:
                result += '-------- %s --------\n' % value
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
    def __str__(self):
        if self.object != None:
            s =  '<%s: %s>'      % (self.__class__.__name__,
                                    self.object.cName(-1)
                                   )
        else:
            s =  '<%s: %s>'      % (self.__class__.__name__,
                                    'None'
                                   )
        #end if
        return s

    def asPid(self):
        if self.object != None:
            #key = self.getattrOnly(constants.PARENT_KEY)
            s =  '<%s:%s.%s.%s>' % (self.__class__.__name__,
                                    self.object.cName(-1),
                                    ValidationResultsContainer.KEY,
                                    self.KEY
                                   )
        else:
            s =  '<%s:%s>'       % (self.__class__.__name__,
                                    'None'
                                   )
        #end if
        return s
    #end def
#end class
#If neded, should be in sml.py because circular imports otherwise
#ValidationResult.SMLhandler = sml.SMLAnyDictHandler(ValidationResult,'ValidationResult',
#                                                    encodeKeys = [constants.OBJECT_KEY],
#                                                    decodeKeys = [constants.OBJECT_KEY]
#                                                   )


def hasValidationResult(theObject,key):
    return (getValidationResult(theObject, key) != None)


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

    # add the result and set the object's reference
    container[key] = result
    if result is not None:
        result[constants.OBJECT_KEY] = theObject
    return False
#end def