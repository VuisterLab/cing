from cing import cingPythonCingDir
from cing.Libs.NTutils import ImportWarning
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTexception
from cing.Libs.NTutils import NTpath
from cing.core.classes import Project
from cing.core.parameters import cingPaths
from cing.core.parameters import plugins
from traceback import format_exc
import glob
import os

# NB This routine gets executed before main.py gets a chance to set the verbosity.
#     If you need to debug this; (getting debug messages) then set verbosity = verbosityDebug in the __init__.py

#print "Now at importPlugin.py"
#NTdebug("This is NTdebug in importPlugin.py")

#-----------------------------------------------------------------------------
# import the plugins
#-----------------------------------------------------------------------------
def importPlugin( pluginName ):
    """
    Import the plugin pluginName present in PluginCode directory.
    Returns None on error
    """
    isInstalled = False

    pluginCodeModule = 'cing.' + cingPaths.plugins
#    moduleName = cingPaths.plugins + '.' + pluginName
    if plugins.has_key(pluginName):
        try:
            plugin = plugins[pluginName]
#            NTdebug("reloading same module just to see it change")
            reload( plugin.module )
        except ImportWarning: # Disable after done debugging; can't use NTdebug yet.
            print "Skipping reload of an optional compound."
        except Exception:
            NTexception('A reload failed for ' + pluginName)
            return None
#    module = __import__( moduleName, globals(), locals(), [] )
#    NTmessage('==> Attempting import plugin ' + pluginName )
# by the manuals words:
# "However, when a non-empty fromlist argument is given, the module named by name is returned."
    pluginCodeModulePackage = None
    try:
        #JFD changed from default to zero which means to only try absolute imports.
        pluginCodeModulePackage = __import__( pluginCodeModule, globals(), locals(), [pluginName])
        isInstalled = True
        NTdebug( "Installed plugin: [%s]" % pluginName )
    except ImportWarning:
        NTdebug( "Skipping import of an optional plugin: [%s]" % pluginName )
        isInstalled = False
    except:
#        traceBackObject = sys.exc_info()[2]
        traceBackString = format_exc()
        NTerror(traceBackString)
        NTerror( 'Failed to import pluginCodeModule: [%s]' % pluginName)
        return None


    pluginModule = None
    if isInstalled:
    #    NTdebug("pluginCodeModulePackage looks like: " + `pluginCodeModulePackage`)
#        NTdebug('importPlugin: ' + pluginName )
        if not hasattr(pluginCodeModulePackage, pluginName):
            NTerror("importPlugin: Expected an attribute pluginName: " + pluginName + " for package: " + `pluginCodeModulePackage`)
            return None
    #     set p to plugin module
        pluginModule = getattr( pluginCodeModulePackage, pluginName )
    #    NTdebug("pluginModule looks like: " + `pluginModule`)

    plugin = NTdict( module = pluginModule, name = pluginName, isInstalled = isInstalled )
    #end try
#    NTdebug('==> Staging plugin ' + pluginName)
    plugins[pluginName] = plugin

    if plugin.isInstalled:
        # update the methods, saves, restores and exports
        for attributeName in ['methods', 'saves', 'restores', 'exports']:
    #        NTdebug("Now working on attribute: " + attributeName)
            plugin[attributeName] = []
            if attributeName in dir(plugin.module):
    #            NTdebug("Now working on attributeName: " + attributeName)
                for function, other in getattr(plugin.module, attributeName):
    #                NTdebug("Now working on function: " + function.__name__)
                    setattr( Project, function.__name__, function )
                    plugin[attributeName].append( (function, other) )
                #end for
            #end if
        #end for
    return plugin
#end def

# get all *.py files in plugin directory excluding __init__
pluginDir = os.path.join(cingPythonCingDir, cingPaths.plugins)
pluginFileList  = glob.glob( os.path.join(pluginDir, '*.py') )
#NTdebug("found plugin file list: " + `pluginFileList`)
pluginFileList.remove( os.path.join( pluginDir, '__init__.py') )

# Moved control to plugin itself without this scattering dep.
#try:
#    import ccpnmr #@UnusedImport
#except:
#    NTdebug('importPlugin: Running CING without CCPN support')
#    pluginFileList.remove( os.path.join( pluginDir, 'Ccpn.py') )

#print "Now at importPlugin.py real job"
for _p in pluginFileList:
    _d,_pname,_e = NTpath(_p)
#    try:
    importPlugin( _pname )
#    except:
#        NTerror('Actual exception: %s [%s]' % (sys.exc_type, sys.exc_info()))
#        raise Exception("Failed to import mandatory plugin: " + _pname)
#end for
del( pluginDir )
del( pluginFileList)
