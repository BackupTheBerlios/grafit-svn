from distutils.core import setup, Extension

setup(name='gl2ps',
      version='1.0',
      ext_modules=[Extension('gl2ps', ['gl2ps_wrap.c', 'gl2ps.c'], libraries=['GL'])],
      )
