"""
Easy organization that allows plugins to be added or removed optionally.

During execution the plugin modules can be reloaded using the python mechanism.

E.g. to reload the aqua plugin use:
reload(cing.PluginCode.aqua)

NB there are no quotes around the module name and outside of ipython the parentheses are required.
"""
#dummy edit