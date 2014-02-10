"""
v3: key validation classes and functions, separate from validation
"""

from cing import constants
from cing.Libs import Adict
from cing.Libs import io


class ValidationResultsContainer(Adict.Adict):
    """v3: Container class for validation results
    key: constants.VALIDATION_KEY
    """
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
            if value != None:
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
            key = self.getattrOnly(constants.KEY_KEY)
            s =  '<%s:%s.%s.%s>' % (self.__class__.__name__,
                                    self.object.cName(-1),
                                    constants.VALIDATION_KEY,
                                    key
                                   )
        else:
            s =  '<%s:%s>'       % (self.__class__.__name__,
                                    'None'
                                   )
        #end if
        return s
    #end def
#end class


def hasValidationResult(object,key):
    return (getValidationResult() != None)


def getValidationResult(object,key):
    """v3:Returns validation result for key or None if not present
    """
    if not hasattr(object, constants.VALIDATION_KEY):
        return None
    validation = getattr(object, constants.VALIDATION_KEY)
    if key not in validation:
        return None
    return validation[key]
#end def


def setValidationResult(object,key,result):
    """v3: Add result to objects validation container instance under key,
    add reverse linkage to result under constants.OBJECT_KEY
    return True on error
    """
#    print( '>>', object, key, result)
    if object == None:
        io.error('setValidationResult: invalid object\n')
        return True
    if key == None:
        io.error('setValidationResult: invalid key\n')
        return True
    #v3: use attribute method so v3 will not 'suffer'
    if not hasattr(object, constants.VALIDATION_KEY):
        setattr(object, constants.VALIDATION_KEY, ValidationResultsContainer())
    validation = getattr(object, constants.VALIDATION_KEY)

    validation[key] = result
    validation.setattrOnly(constants.OBJECT_KEY, object)

    if result != None:
        result[constants.OBJECT_KEY] = object
        result.setattrOnly(constants.KEY_KEY, key)
    return False
#end def