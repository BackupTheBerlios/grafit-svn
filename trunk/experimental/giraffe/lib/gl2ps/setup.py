from distutils.core import setup, Extension
import platform

if platform.system() == 'Windows':
    libs = ['OpenGL32']
elif platform.system() == 'Linux':
    libs = ['GL']

setup(name='pygl2ps',
      version='0.1',
      packages=['gl2ps'],
      package_dir={'gl2ps':''},

      ext_modules=[Extension('_gl2ps', 
                             ['src/gl2ps_wrap.c', 'src/gl2ps.c',], 
                             include_dirs=['src'],
                             libraries=libs,
                             )], )
