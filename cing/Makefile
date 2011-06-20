# CING makefile
# gv  June 10, 2008
# jfd 2011-06-17
#

#all:	install test fails because cython needs to be found.
		
install:
	@echo "==> Installing CING setup script ..."
	-/bin/rm -f cing.csh
	python python/cing/setup.py -tcsh

build_cython:
	@echo "==> Building CING cython dependencies ..."
	-/bin/rm -f python/cing/Libs/cython/superpose.so
	-/bin/rm -f python/cing/Libs/cython/superpose.c
	cd python/cing/Libs/cython; python compile.py build_ext --inplace

test:
	python -u python/cing/main.py --testQ
