all: render.so
	@make -C lib/ftgl

render.so: render.pyx
	@echo compiling 'render' pyrex extension...
	@pyrexc render.pyx
	@gcc -fPIC -I/usr/include/python2.3/ -lGL -shared render.c -o render.so

clean:
	@rm render.so
	@make -C ftgl clean
