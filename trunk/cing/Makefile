# CING makefile
# gv  June 10, 2008
# jfd 2011-06-17
#

all:	install test
		
install:
	@echo "==> Installing CING setup script ..."
	-/bin/rm -f cing.sh
	-/bin/rm -f python/cing/Libs/cython/superpose.so
	-/bin/rm -f python/cing/Libs/cython/superpose.c
	python python/cing/setup.py -sh
	@echo "==> Building CING cython dependencies ..."
	cd python/cing/Libs/cython; python compile.py build_ext --inplace

test:
	python -u python/cing/main.py --testQ

