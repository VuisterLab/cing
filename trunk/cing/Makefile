# CING makefile
# gv  June 10, 2008
# jfd 2011-06-17
#

#all:	install test fails because cython needs to be found.
		
install:
	@echo "==> Installing CING setup script ..."
	-/bin/rm -f cing.csh
	python python/cing/setupCing.py -tcsh

build_cython:
	@echo "==> Building CING cython dependencies ..."
	-/bin/rm -f python/cing/Libs/cython/superpose.so
	-/bin/rm -f python/cing/Libs/cython/superpose.c
	cd python/cing/Libs/cython; python compile.py build_ext --inplace

test:
	python -u python/cing/main.py --testQ

	
#sloccount:
#	sloccount --duplicates --wide --details divergence/*.py divergence/test/*.py > sloccount.sc

nose:
#	nosetests --with-xunit --with-coverage --verbose --where=python/cing/core/test
	nosetests --with-xunit --with-coverage --verbose --cover-package=cing --where=python/cing
#	nosetests --testmatch=test_.+.py
#	coverage xml

#pylint:
#	pylint --max-line-length=120 --disable="E0602,W0511" -f parseable --include-ids=y divergence > pylint.txt || exit 0