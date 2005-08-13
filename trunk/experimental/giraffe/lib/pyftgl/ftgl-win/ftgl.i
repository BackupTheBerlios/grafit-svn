%module ftgl
%{
/* Includes the header in the wrapper code */
/*#include "/usr/include/FTGL/FTGL.h" */
#include "FTGL/include/FTFace.h"
#include "FTGL/include/FTFont.h"
#include "FTGL/include/FTGLOutlineFont.h"
#include "FTGL/include/FTGLPolygonFont.h"
#include "FTGL/include/FTGLTextureFont.h"
#include "FTGL/include/FTGLBitmapFont.h"
#include "FTGL/include/FTGLPixmapFont.h"
%}

/* Parse the header file to generate wrappers */
%include "FTGL/include/FTGL.h"
%include "FTGL/include/FTFace.h"
%include "FTGL/include/FTFont.h"
%include "FTGL/include/FTGLOutlineFont.h"
%include "FTGL/include/FTGLPolygonFont.h"
%include "FTGL/include/FTGLTextureFont.h"
%include "FTGL/include/FTGLBitmapFont.h"
%include "FTGL/include/FTGLPixmapFont.h"
