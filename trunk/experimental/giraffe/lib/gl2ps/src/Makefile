wrapper:
	@echo "creating gl2ps wrapper..."
	swig -shadow -python gl2ps.i
	mv gl2ps.py ../__init__.py
#	@echo "compiling gl2ps wrapper..."
#	@gcc gl2ps_wrap.c -shared -o _gl2ps.so gl2ps.c -I/usr/include/python2.4 -lGL

#clean:
#	rm -f _gl2ps.so gl2ps.py gl2ps_wrap.c *.pyc
