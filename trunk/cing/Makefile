# CING makefile
# gv 10 June 2008
#

install:
	@echo "==> Installing CING setup script ..."
	@python python/cing/setup.py

superpose:
	@echo "==> Installing the cython dependency"
	@/bin/rm -f python/cing/Libs/cython/superpose.so
	@/bin/rm -f python/cing/Libs/cython/superpose.c
	@cd python/cing/Libs/cython; python compile.py build_ext --inplace

test:
	python python/cing/main.py --test -v 0

