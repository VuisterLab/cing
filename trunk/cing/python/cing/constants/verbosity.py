__author__ = 'geerten'
#-----------------------------------------------------------------------------
# Verbosity settings: How much text is printed to stdout/stderr streams
# Follows exact same int codes as Wattos.
# Reference to it as cing.verbosity if you want to see non-default behavior
#-----------------------------------------------------------------------------
nothing  = 0 # Even errors will be suppressed
error    = 1 # show only errors
warning  = 2 # show errors and warnings
output   = 3 # and regular output DEFAULT
detail   = 4 # show more details
debug    = 9 # add debugging info (not recommended for casual user)
default  = output

###### legacy definitions Jurgen local override
try:
    from cing.localConstants import verbosityDefault as default
except:
    pass
#end try
# verbosity =  default
# try:
#     from cing.localConstants import verbosity
# except:
#     pass
# #end try