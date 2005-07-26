from distutils.core import setup, Extension

setup(name='gl2ps',
      version='0.1',
      packages=['gl2ps'],
      package_dir={'gl2ps':''},

      ext_modules=[Extension('_gl2ps', 
                             ['src/gl2ps_wrap.c', 'src/gl2ps.c',], 
                             include_dirs=['src'],
                             libraries=['GL'],
                             )],

      )
