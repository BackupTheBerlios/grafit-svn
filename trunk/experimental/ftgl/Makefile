wrapper:
	@echo "creating wrapper..."
	@swig -c++ -python ftgl.i
	@echo "compiling wrapper..."
	@c++ ftgl_wrap.cxx -shared -o _ftgl.so -I/usr/include/python2.3 \
					-I/usr/include/freetype2 -lfreetype -lftgl -lGL -lGLU

clean:
	rm -f _ftgl.so ftgl.py ftgl_wrap.cxx *.pyc
