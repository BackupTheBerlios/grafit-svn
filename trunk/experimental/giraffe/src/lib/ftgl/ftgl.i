%module ftgl
%{
/* Includes the header in the wrapper code */
/*#include "/usr/include/FTGL/FTGL.h" */
#include "/usr/include/FTGL/FTFace.h"
#include "/usr/include/FTGL/FTFont.h"
#include "/usr/include/FTGL/FTGLOutlineFont.h"
#include "/usr/include/FTGL/FTGLPolygonFont.h"
#include "/usr/include/FTGL/FTGLTextureFont.h"
#include "/usr/include/FTGL/FTGLBitmapFont.h"
#include "/usr/include/FTGL/FTGLPixmapFont.h"
%}

/* Parse the header file to generate wrappers */
%include "/usr/include/FTGL/FTGL.h"
%include "/usr/include/FTGL/FTFace.h"
%include "/usr/include/FTGL/FTFont.h"
%include "/usr/include/FTGL/FTGLOutlineFont.h"
%include "/usr/include/FTGL/FTGLPolygonFont.h"
%include "/usr/include/FTGL/FTGLTextureFont.h"
%include "/usr/include/FTGL/FTGLBitmapFont.h"
%include "/usr/include/FTGL/FTGLPixmapFont.h"
