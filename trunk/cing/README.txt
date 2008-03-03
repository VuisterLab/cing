#------------------------------------------------------------------------------
 SETUP
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
Go to your CING installations directory. This directory will be identified by the
CINGROOT environment variable once the below setup is done. Type:

python python/cing/setup.py

This generates cing.csh or cing.sh in the current directory that you need to check 
and adjust if needed. Then source it in your .cshrc or .bashrc file
 
The setup.py script uses 'which xplor' etc. to determine the various locations for
executables; make sure it is in your path when you run setup. 

Setup instructions for working with CING in Eclipse/PyDev are available in:
Documentation/setupEclipse/development_installation_eclipse.html

#------------------------------------------------------------------------------
To get help, more help, or test do:
> cing -h
> cing -doc
> cing --test -v 0