# CING makefile
# gv  June 10, 2008
# jfd 2011-06-17
#

all:	clean install cython sloccount pylint nose
		
clean:
	@echo "Cleaning up CING installation"
	-/bin/rm -f cing.csh
	
install:
	@echo "==> Installing CING setup script ..."
	-/bin/rm -f cing.csh
	python python/cing/setupCing.py -tcsh

cython:
	@echo "==> Building CING cython dependencies ..."
	-/bin/rm -f python/cing/Libs/cython/superpose.so
	-/bin/rm -f python/cing/Libs/cython/superpose.c
	cd python/cing/Libs/cython; python compile.py build_ext --inplace

# Using nose instead.
#test:
#	python -u python/cing/main.py --testQ -c 1

sloccount:
	-/bin/rm -f sloccount.sc
	-sloccount --duplicates --wide --details python src > sloccount.sc

pylint:
	# CING will run pylint on individual files as not to exceed open file limit.
	-cd python; python -u cing/main.py --pylint pylint.txt
	
# Next fails in recursion with old version of pylint 0.20.0 but works fine with version 0.23.0
pylint_old:
	-/bin/rm -f python/pylint.txt
	-cd python; pylint --rcfile ../.pylintrc --report=no cing.core                                          > pylint.txt || exit 0
	-cd python; pylint --rcfile ../.pylintrc --report=no cing.Database                                     >> pylint.txt || exit 0
	-cd python; pylint --rcfile ../.pylintrc --report=no cing.Libs                                         >> pylint.txt || exit 0
	-cd python; pylint --rcfile ../.pylintrc --report=no cing.NRG                                          >> pylint.txt || exit 0
	-cd python; pylint --rcfile ../.pylintrc --report=no cing.PluginCode                                   >> pylint.txt || exit 0
	-cd python; pylint --rcfile ../.pylintrc --report=no cing.Scripts                                      >> pylint.txt || exit 0
	-cd python; pylint --rcfile ../.pylintrc --report=no cing.Talos                                        >> pylint.txt || exit 0
		
# Next fails with old version of nosetest 0.10.4 but works fine with version 1.0.0
nose:
	# Write the .coverage and nosetest.xml
	# Uses .coveragerc
	-/bin/rm -f nosetests.xml coverage.xml .coverage
	-nosetests --with-xunit --with-coverage --verbose --cover-package=cing --where=python/cing
	# Convert .coverage to coverage.xml. 
	#Needs Coverage.py, version 3.4+.  http://nedbatchelder.com/code/coverage
	-coverage xml
	
test:
	# This Makefile test -does- need to succeed for the make to be successful.
	python -u python/cing/main.py --testQ

