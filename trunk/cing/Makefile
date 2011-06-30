# CING makefile
# gv  June 10, 2008
# jfd 2011-06-17
#

all:	clean install build_cython sloccount pylint nose
		
clean:
	@echo "Cleaning up CING installation"
	-/bin/rm -f cing.csh
	
install:
	@echo "==> Installing CING setup script ..."
	-/bin/rm -f cing.csh
	python python/cing/setupCing.py -tcsh

build_cython:
	@echo "==> Building CING cython dependencies ..."
	-/bin/rm -f python/cing/Libs/cython/superpose.so
	-/bin/rm -f python/cing/Libs/cython/superpose.c
	cd python/cing/Libs/cython; python compile.py build_ext --inplace

# Using nose instead.
#test:
#	python -u python/cing/main.py --testQ -c 1

sloccount:
	-/bin/rm -f sloccount.sc
	sloccount --duplicates --wide --details python src > sloccount.sc

pylint:
	-/bin/rm -f python/pylint.txt
	-cd python; pylint --rcfile .pylintrc cing > pylint.txt || exit 0
		
nose:
	# Write the .coverage and nosetest.xml
	# Uses .coveragerc
	-/bin/rm -f nosetests.xml coverage.xml .coverage
	-nosetests --with-xunit --with-coverage --verbose --cover-package=cing --where=python/cing
	# Convert .coverage to coverage.xml
	-coverage xml

