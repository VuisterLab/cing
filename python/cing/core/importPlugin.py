from cing import cingPythonCingDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.parameters import cingPaths
from cing.core.parameters import plugins
from nose.plugins.skip import SkipTest
import glob

# NB This routine gets executed before main.py gets a chance to set the verbosity.
#     If you need to debug this; (getting debug messages) then set verbosity = verbosityDebug in the __init__.py

#print "Now at importPlugin.py"
#nTdebug("This is nTdebug in importPlugin.py")

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
#            nTdebug("reloading same module just to see it change")
            reload( plugin.module )
        except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
            nTmessage("Skipping reload of an optional compound (please recode to use SkipTest): %s" % extraInfo)
            # Internally we need to know if we're called by nosetests or by regular call.           
        except SkipTest, extraInfo:
            nTmessage("Skipping reload report of an optional compound: %s" % extraInfo)            
        except Exception:
            nTtracebackError()
            nTexception('A reload failed for ' + pluginName)
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
#        nTdebug( "Installed plugin: [%s]" % pluginName )
    except ImportWarning:
        nTdebug( "Skipping import of an optional plugin: [%s] (please recode to use SkipTest)" % pluginName )
        isInstalled = False
    except SkipTest:
        nTdebug("Skipping import of an optional plugin: [%s]" % pluginName )            
    except:
        nTtracebackError()
        nTerror( 'Failed to import pluginCodeModule: [%s]' % pluginName)
        return None


    pluginModule = None
    if isInstalled:
    #    nTdebug("pluginCodeModulePackage looks like: " + repr(pluginCodeModulePackage))
#        nTdebug('importPlugin: ' + pluginName )
        if not hasattr(pluginCodeModulePackage, pluginName):
            nTerror("importPlugin: Expected an attribute pluginName: " + pluginName + " for package: " + repr(pluginCodeModulePackage))
            return None
    #     set p to plugin module
        pluginModule = getattr( pluginCodeModulePackage, pluginName )
    #    nTdebug("pluginModule looks like: " + repr(pluginModule))

    plugin = NTdict( module = pluginModule, name = pluginName, isInstalled = isInstalled )
    #end try
#    nTdebug('==> Staging plugin ' + pluginName)
    plugins[pluginName] = plugin

    if plugin.isInstalled:
        # update the methods, saves, restores and exports
        for attributeName in ['methods', 'saves', 'restores', 'exports']:
    #        nTdebug("Now working on attribute: " + attributeName)
            plugin[attributeName] = []
            if attributeName in dir(plugin.module):
    #            nTdebug("Now working on attributeName: " + attributeName)
                for function, other in getattr(plugin.module, attributeName):
    #                nTdebug("Now working on function: " + function.__name__)
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
#nTdebug("found plugin file list: " + repr(pluginFileList))
pluginFileList.remove( os.path.join( pluginDir, '__init__.py') )

# Moved control to plugin itself without this scattering dep.
#try:
#    import ccpnmr #@UnusedImport
#except:
#    nTdebug('importPlugin: Running CING without CCPN support')
#    pluginFileList.remove( os.path.join( pluginDir, 'Ccpn.py') )

#print "Now at importPlugin.py real job"
for _p in pluginFileList:
    _d,_pname,_e = nTpath(_p)
#    if _pname.find('Whatif')>=0:
#        nTdebug("Skipping import of plugin Whatif")
#        continue
#    try:
    importPlugin( _pname )
#    except:
#        nTerror('Actual exception: %s [%s]' % (sys.exc_type, sys.exc_info()))
#        raise Exception("Failed to import mandatory plugin: " + _pname)
#end for
del( pluginDir )
del( pluginFileList)
