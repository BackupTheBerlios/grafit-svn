from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(name="buf", 
      ext_modules=[Extension("buf", ["buf.pyx"], libraries=['GL'])],
      cmdclass={'build_ext': build_ext })
