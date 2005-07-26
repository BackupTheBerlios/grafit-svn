from distutils.core import setup
setup(name='gl2ps',
      version='0.1',
      ext_modules=[Extension('foo', ['foo.c'])],
      )
