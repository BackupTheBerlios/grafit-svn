from distutils.core import setup, Extension
setup(name='ftgl',
      version='0.1',
      ext_modules=[Extension('_ftgl', ['foo.c'])],
                          -I/usr/include/freetype2 -lfreetype -lftgl -lGL -lGLU

      )
