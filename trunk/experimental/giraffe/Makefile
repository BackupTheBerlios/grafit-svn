render.so:
	@echo compiling extension...
	@pyrexc render.pyx
	@gcc -fPIC -I/usr/include/python2.3/ -lGL -shared render.c -o render.so
	@make -C ftgl

clean:
	@rm render.so
	@make -C ftgl clean
