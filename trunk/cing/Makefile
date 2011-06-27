# CING makefile
# gv  June 10, 2008
# jfd 2011-06-17
#

#all:	install test fails because cython needs to be found.
		
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

nose:
	# Write the .coverage and nosetest.xml
	nosetests --with-xunit --with-coverage --verbose --cover-package=cing --where=python/cing
	# Convert .coverage to coverage.xml
	coverage xml

pylint:
	cd python; pylint --rcfile .pylintrc cing > pylint.txt || exit 0
	
sloccount:
	sloccount --duplicates --wide --details python src > sloccount.sc
