from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(name="render", 
      ext_modules=[Extension("render", ["render.pyx"], libraries=['GL'])],
      cmdclass={'build_ext': build_ext })
