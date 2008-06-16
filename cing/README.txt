#------------------------------------------------------------------------------
# SETUP
#------------------------------------------------------------------------------

Go to your CING installation directory. This directory will be identified by the
CINGROOT environment variable once the below setup is done. Type:

make install

This generates cing.csh or cing.sh in the current directory that you need to check
and adjust if needed. Then source it in your .cshrc or .bashrc file.

The installation uses 'which xplor' etc. to determine the various locations for
executables; make sure it is in your path when you run setup.

#------------------------------------------------------------------------------
# Testing
#------------------------------------------------------------------------------
Go to your CING installation directory.

make test

#------------------------------------------------------------------------------
# Getting help
#------------------------------------------------------------------------------
> cing -h
> cing -doc

#------------------------------------------------------------------------------
# Working with eclipse
#------------------------------------------------------------------------------
Setup instructions for working with CING in Eclipse/PyDev are available in:
Documentation/setupEclipse/development_installation_eclipse.html

