# From: http://www.swig.org/tutorial.html

# For tcl
gcc -shared example.o example_wrap.o -o example.so -I/opt/local/include -L/opt/local/lib -ltcl

# For python
# create the example_wrap.c
swig -python example.i
#gcc -c example.c example_wrap.c -I/opt/local/Library/Frameworks/Python.framework/Versions/2.6/include/python2.6/

# Compile both c files and ignore warnings
cc -c `python-config --cflags` example.c example_wrap.c
# create .so
cc -bundle `python-config --ldflags` example.o example_wrap.o -o _example.so

ipython
    In [1]: import example
    
    In [2]: example.fact(3)
    Out[2]: 6
    
    
    
Now for nmv:

# manually done:
#	cd nr; gcc -c nrutil.c -o nrutil.o


swig -python nmv.i
cc -c `python-config --cflags` nmv.c nmv_wrap.c
# create .so
cc -bundle `python-config --ldflags` nmv.o nmv_wrap.o -o _nmv.so

