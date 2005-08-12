from distutils.core import setup
from distutils.extension import Extension
#from Pyrex.Distutils import build_ext

setup(name="graph_render", 
      ext_modules=[Extension("graph_render", ["graph_render.c"], 
		libraries=['OpenGL32'])],
)
#      cmdclass={'build_ext': build_ext })
