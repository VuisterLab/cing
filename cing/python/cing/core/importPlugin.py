from cing.definitions import cingDefinitions
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.parameters import plugins
from nose.plugins.skip import SkipTest

# NB This routine gets executed before main.py gets a chance to set the verbosity.
#     If you need to debug this; (getting debug messages) then set verbosity = 9 in the localConstants.py file in
#     CINGROOT/python/cing directory

#nTdebug("This is nTdebug in importPlugin.py")

#-----------------------------------------------------------------------------
# import the plugins
#-----------------------------------------------------------------------------
def importPlugin( pluginName ):
    """
    Import the plugin pluginName present in PluginCode directory.
    Adds reference to global plugins dict
    Returns None on error
    """
    isInstalled = False

    pluginCodeModule = cingDefinitions.pluginCode
#    moduleName = cingPaths.plugins + '.' + pluginName
    if plugins.has_key(pluginName):
        try:
            plugin = plugins[pluginName]
#            nTdebug("reloading same module just to see it change")
            reload( plugin.module )
        except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
            nTmessage("importPlugin: Skipping reload of an optional compound (please recode to use SkipTest): %s" % extraInfo)
            # Internally we need to know if we're called by nosetests or by regular call.
        except SkipTest, extraInfo:
            nTmessage("importPlugin: Skipping reload report of an optional compound: %s" % extraInfo)
        except Exception:
            nTtracebackError()
            nTexception('importPlugin: A reload failed for ' + pluginName)
            return None
#    module = __import__( moduleName, globals(), locals(), [] )
#    nTmessage('==> Attempting import plugin ' + pluginName )
# by the manuals words:
# "However, when a non-empty fromlist argument is given, the module named by name is returned."
    pluginCodeModulePackage = None
    try:
        #JFD changed from default to zero which means to only try absolute imports.
        pluginCodeModulePackage = __import__( pluginCodeModule, globals(), locals(), [pluginName])
        isInstalled = True
        nTdebug( "importPlugin: Installed plugin: [%s]" % pluginName )
    except ImportWarning:
        nTdebug( "importPlugin: Skipping import of an optional plugin: [%s] (please recode to use SkipTest)" % pluginName )
        isInstalled = False
    except SkipTest:
        nTdebug("importPlugin: Skipping import of an optional plugin: [%s]" % pluginName )
    except:
        nTtracebackError()
        nTerror( 'importPlugin: Failed to import pluginCodeModule: [%s]' % pluginName)
        return None
    #end try

    pluginModule = None
    if isInstalled:
        if not hasattr(pluginCodeModulePackage, pluginName):
            nTerror("importPlugin: Expected an attribute pluginName: " + pluginName + " for package: " + repr(pluginCodeModulePackage))
            return None
        pluginModule = getattr( pluginCodeModulePackage, pluginName )
        #end if
    #end if

    plugin = NTdict( module = pluginModule, name = pluginName, isInstalled = isInstalled )
    plugins[pluginName] = plugin

    if plugin.isInstalled:
        # update the methods, saves, restores and exports
        for attributeName in ['methods', 'saves', 'restores', 'exports']:
            plugin[attributeName] = []
            if attributeName in dir(plugin.module):
                for function, other in getattr(plugin.module, attributeName):
                    setattr( Project, function.__name__, function )
                    plugin[attributeName].append( (function, other) )
                #end for
            #end if
        #end for
    #end if
    return plugin
#end def

# do all *.py files in plugin directory excluding __init__
# GWV 30 Jan 2014: using CingDefinitions class instance
for _p in (cingDefinitions.pluginCodePath / '*.py').glob():
    _d,_pname,_e = _p.split3()
    #print '>>',_pname
    if _pname != '__init__':
        importPlugin( _pname )
#end for
