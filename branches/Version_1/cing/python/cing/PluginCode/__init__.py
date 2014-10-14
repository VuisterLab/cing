"""
Easy organization that allows plugins to be added or removed optionally.

During execution the plugin modules can be reloaded using the python mechanism.


Plugins for running a external program should use the following setup:

- get status settings dict:

status = project.getStatusDict( key, **optionalSettings )

- implement:

runProgram( project, optionalObject = None )

remove any object from the data
run and parse results

==>
settings.completed = True
settings.parsed = False
settings.present = False
settings.directory = directory relative to project.validationPath()
settings.runVersion = current plugin version

directories get overwritten

parseProgram( project, optionalObject = None )
==>
settings.parsed = True
settings.present = True

saveProgram( project, optionalObject = None )
==>
settings.saved = True
settings.savedVersion = current plugin version
settings.smlFile = file in Data/Plugins

restoreProgram( project, optionalObject = None )
==>
settings.present = True

settings:
completed: Program was run successfully
parsed: Program output was parsed successfully; i.e parse can be called if completed == True -> implies present = True
Present: Program data are in the datamodel
Saved: Data have been saved to sml in Data/Plugins; i.e. restore can be called in saved = True

"""
