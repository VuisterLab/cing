# Premise #
First install the dependencies as described: MacInstallationGuide or LinuxInstallationGuide

# Setup script #
Replace $CINGROOT with your CING installation directory.
```
python $CINGROOT/python/cing/setup.py
```
Will look for installed software and puts the settings into a .csh/.sh to be sourced from your setup. Add it to your setup .cshrc or equivalent.

It will also generate an alias to run cing:

Now compile the Cython dependency following the note presented by running the setup.py script.
```
 There is another dependency; cython. Please install it and run:
 cd $CINGROOT/python/cing/Libs/cython; python compile.py build_ext --inplace
```
Ask Chris how to compile it on Linux. For Mac we have included the code in:
$CINGROOT/dis/Cython.

# Test setup #
```
cing --test -v 0
```
If all is fine it should only list ok at the end of each test.

# Optional installs #
A lot of functionality comes from optional installations; see OptionalInstallNotes.