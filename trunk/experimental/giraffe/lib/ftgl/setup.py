from distutils.core import setup, Extension
import platform
system = platform.system()

if system == 'Windows':
    opengl_libs = ['opengl32', 'glu32']
    ftincludedirs = ['f:/program files/freetype/include', 
                     'f:/program files/freetype/include/freetype2']
    ftlibdirs = ['f:/program files/freetype/lib']
elif system == 'Linux':
    opengl_libs = ['GL', 'GLU']
    ftincludedirs = ['/usr/include/freetype2']
    ftlibdirs = []


ftgl_sources = [ 'FTGL/src/FTBitmapGlyph.cpp', 'FTGL/src/FTCharmap.cpp',
                 'FTGL/src/FTContour.cpp', 'FTGL/src/FTExtrdGlyph.cpp',
                 'FTGL/src/FTFace.cpp', 'FTGL/src/FTFont.cpp',
                 'FTGL/src/FTGLBitmapFont.cpp', 'FTGL/src/FTGLExtrdFont.cpp',
                 'FTGL/src/FTGLOutlineFont.cpp', 'FTGL/src/FTGLPixmapFont.cpp',
                 'FTGL/src/FTGLPolygonFont.cpp', 'FTGL/src/FTGLTextureFont.cpp',
                 'FTGL/src/FTGlyph.cpp', 'FTGL/src/FTGlyphContainer.cpp',
                 'FTGL/src/FTLibrary.cpp', 'FTGL/src/FTOutlineGlyph.cpp',
                 'FTGL/src/FTPixmapGlyph.cpp', 'FTGL/src/FTPoint.cpp',
                 'FTGL/src/FTPolyGlyph.cpp', 'FTGL/src/FTSize.cpp',
                 'FTGL/src/FTTextureGlyph.cpp', 'FTGL/src/FTVectoriser.cpp',]


setup(name='pyftgl',
      version='0.1',
      packages=['ftgl'],
      package_dir={'ftgl':''},
      ext_modules=[Extension('_ftgl', ['ftgl_wrap.cxx' ] + ftgl_sources,
                             include_dirs = ftincludedirs + ['FTGL/include'],
                             libraries = opengl_libs + ['freetype'],
                             library_dirs = ftlibdirs),  ])
