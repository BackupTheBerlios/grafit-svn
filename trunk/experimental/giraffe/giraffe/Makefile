all: graph_render.so

graph_render.so: graph_render.pyx
	@echo compiling 'graph_render' pyrex extension...
	@pyrexc graph_render.pyx
	@gcc -fPIC -I/usr/include/python2.4/ -lGL -shared graph_render.c -o graph_render.so
	@chmod -x graph_render.so

clean:
	@rm -f graph_render.so
	@rm -f *.pyc
