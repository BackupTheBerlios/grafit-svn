all: render.so
	@make -C ftgl

render.so:
	@echo compiling 'render' pyrex extension...
	@pyrexc render.pyx
	@gcc -fPIC -I/usr/include/python2.3/ -lGL -shared render.c -o render.so

clean:
	@rm render.so
	@make -C ftgl clean
