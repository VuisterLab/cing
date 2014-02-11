from cing import plugins
from cing import definitions as cdefs
from cing.Libs import Adict
from cing.Libs import NTutils as ntu

from cing.core.classes import Project
from nose.plugins.skip import SkipTest

# NB This routine gets executed before main.py gets a chance to set the verbosity.
#     If you need to debug this; (getting debug messages) then set verbosity = 9 in the localConstants.py file in
#     CINGROOT/python/cing directory

#class PlugIns( cing.Libs.Adict.Adict ):
# CANNOT wrap into a class because imports get circular as cing.plugins needs to be defined earlier
##end class

#-----------------------------------------------------------------------------
# import the plugins
#-----------------------------------------------------------------------------
def importPlugin( pluginCodeModule, pluginName ):
    """
    Import the plugin pluginName present in PluginCode directory.
    Adds reference to global plugins dict
    Returns None on error
    """
    isInstalled = False
    if plugins.has_key(pluginName):
        try:
            plugin = plugins[pluginName]
#            nTdebug("reloading same module just to see it change")
            reload(plugin.module)
        except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
            ntu.nTmessage("importPlugin: Skipping reload of an optional compound (please recode to use SkipTest): %s" % extraInfo)
            # Internally we need to know if we're called by nosetests or by regular call.
        except SkipTest, extraInfo:
            ntu.nTmessage("importPlugin: Skipping reload report of an optional compound: %s" % extraInfo)
        except Exception:
            ntu.nTtracebackError()
            ntu.nTexception('importPlugin: A reload failed for ' + pluginName)
            return None
#    module = __import__( moduleName, globals(), locals(), [] )
#    ntu.nTmessage('==> Attempting import plugin ' + pluginName )
# by the manuals words:
# "However, when a non-empty fromlist argument is given, the module named by name is returned."
    pluginCodeModulePackage = None
    try:
        #JFD changed from default to zero which means to only try absolute imports.
        pluginCodeModulePackage = __import__(pluginCodeModule, globals(), locals(), [pluginName])
        isInstalled = True
        ntu.nTdebug("importPlugin: Installed plugin: [%s]" % pluginName)
    except ImportWarning:
        ntu.nTdebug("importPlugin: Skipping import of an optional plugin: [%s] (please recode to use SkipTest)" % pluginName)
        isInstalled = False
    except SkipTest:
        ntu.nTdebug("importPlugin: Skipping import of an optional plugin: [%s]" % pluginName)
    except:
        ntu.nTtracebackError()
        ntu.nTerror('importPlugin: Failed to import pluginCodeModule: [%s]' % pluginName)
        return None
    #end try

    pluginModule = None
    if isInstalled:
        if not hasattr(pluginCodeModulePackage, pluginName):
            ntu.nTerror("importPlugin: Expected an attribute pluginName: " + pluginName + " for package: " + repr(pluginCodeModulePackage))
            return None
        pluginModule = getattr(pluginCodeModulePackage, pluginName)
        #end if
    #end if

    plugin = Adict.Adict(module = pluginModule, name = pluginName, isInstalled = isInstalled, version = None)
    plugins[pluginName] = plugin

    if plugin.isInstalled:
        # update the version, methods, saves, restores and exports, add them to Project class
        if hasattr(plugin.module, '__version__'):
            plugin.version = getattr(plugin.module, '__version__')
        else:
            # old code
            plugin.version = 0.95
        for attributeName in ['methods', 'saves', 'restores', 'exports']:
            plugin[attributeName] = []
            if hasattr(plugin.module, attributeName):
                for function, other in getattr(plugin.module, attributeName):
                    # add the functions to the Project class
                    setattr(Project, function.__name__, function)
                    # store the function in the plugin for later usage on Project.save() and Project.restore()
                    plugin[attributeName].append((function, other))
                #end for
            #end if
        #end for
    #end if
    return plugin
#end def

def importPlugins():
    # do all *.py files in plugin directory excluding __init__
    # GWV 30 Jan 2014: using CingDefinitions class instance
    for _p in (cdefs.cingDefinitions.pluginPath / '*.py').glob():
        _d,_pname,_e = _p.split3()
        #print '>>',_pname
        if _pname != '__init__':
            importPlugin(cdefs.cingDefinitions.pluginCode, _pname)
    #end for
#end def
