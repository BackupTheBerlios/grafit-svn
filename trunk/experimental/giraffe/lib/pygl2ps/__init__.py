# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _gl2ps

def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static) or hasattr(self,name) or (name == "thisown"):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


GL2PS_MAJOR_VERSION = _gl2ps.GL2PS_MAJOR_VERSION
GL2PS_MINOR_VERSION = _gl2ps.GL2PS_MINOR_VERSION
GL2PS_PATCH_VERSION = _gl2ps.GL2PS_PATCH_VERSION
GL2PS_VERSION = _gl2ps.GL2PS_VERSION
GL2PS_PS = _gl2ps.GL2PS_PS
GL2PS_EPS = _gl2ps.GL2PS_EPS
GL2PS_TEX = _gl2ps.GL2PS_TEX
GL2PS_PDF = _gl2ps.GL2PS_PDF
GL2PS_NO_SORT = _gl2ps.GL2PS_NO_SORT
GL2PS_SIMPLE_SORT = _gl2ps.GL2PS_SIMPLE_SORT
GL2PS_BSP_SORT = _gl2ps.GL2PS_BSP_SORT
GL2PS_SUCCESS = _gl2ps.GL2PS_SUCCESS
GL2PS_INFO = _gl2ps.GL2PS_INFO
GL2PS_WARNING = _gl2ps.GL2PS_WARNING
GL2PS_ERROR = _gl2ps.GL2PS_ERROR
GL2PS_NO_FEEDBACK = _gl2ps.GL2PS_NO_FEEDBACK
GL2PS_OVERFLOW = _gl2ps.GL2PS_OVERFLOW
GL2PS_UNINITIALIZED = _gl2ps.GL2PS_UNINITIALIZED
GL2PS_NONE = _gl2ps.GL2PS_NONE
GL2PS_DRAW_BACKGROUND = _gl2ps.GL2PS_DRAW_BACKGROUND
GL2PS_SIMPLE_LINE_OFFSET = _gl2ps.GL2PS_SIMPLE_LINE_OFFSET
GL2PS_SILENT = _gl2ps.GL2PS_SILENT
GL2PS_BEST_ROOT = _gl2ps.GL2PS_BEST_ROOT
GL2PS_OCCLUSION_CULL = _gl2ps.GL2PS_OCCLUSION_CULL
GL2PS_NO_TEXT = _gl2ps.GL2PS_NO_TEXT
GL2PS_LANDSCAPE = _gl2ps.GL2PS_LANDSCAPE
GL2PS_NO_PS3_SHADING = _gl2ps.GL2PS_NO_PS3_SHADING
GL2PS_NO_PIXMAP = _gl2ps.GL2PS_NO_PIXMAP
GL2PS_USE_CURRENT_VIEWPORT = _gl2ps.GL2PS_USE_CURRENT_VIEWPORT
GL2PS_COMPRESS = _gl2ps.GL2PS_COMPRESS
GL2PS_NO_BLENDING = _gl2ps.GL2PS_NO_BLENDING
GL2PS_TIGHT_BOUNDING_BOX = _gl2ps.GL2PS_TIGHT_BOUNDING_BOX
GL2PS_POLYGON_OFFSET_FILL = _gl2ps.GL2PS_POLYGON_OFFSET_FILL
GL2PS_POLYGON_BOUNDARY = _gl2ps.GL2PS_POLYGON_BOUNDARY
GL2PS_LINE_STIPPLE = _gl2ps.GL2PS_LINE_STIPPLE
GL2PS_BLEND = _gl2ps.GL2PS_BLEND
GL2PS_TEXT_C = _gl2ps.GL2PS_TEXT_C
GL2PS_TEXT_CL = _gl2ps.GL2PS_TEXT_CL
GL2PS_TEXT_CR = _gl2ps.GL2PS_TEXT_CR
GL2PS_TEXT_B = _gl2ps.GL2PS_TEXT_B
GL2PS_TEXT_BL = _gl2ps.GL2PS_TEXT_BL
GL2PS_TEXT_BR = _gl2ps.GL2PS_TEXT_BR
GL2PS_TEXT_T = _gl2ps.GL2PS_TEXT_T
GL2PS_TEXT_TL = _gl2ps.GL2PS_TEXT_TL
GL2PS_TEXT_TR = _gl2ps.GL2PS_TEXT_TR

gl2psBeginPage = _gl2ps.gl2psBeginPage

gl2psEndPage = _gl2ps.gl2psEndPage

gl2psSetOptions = _gl2ps.gl2psSetOptions

gl2psBeginViewport = _gl2ps.gl2psBeginViewport

gl2psEndViewport = _gl2ps.gl2psEndViewport

gl2psText = _gl2ps.gl2psText

gl2psTextOpt = _gl2ps.gl2psTextOpt

gl2psDrawPixels = _gl2ps.gl2psDrawPixels

gl2psEnable = _gl2ps.gl2psEnable

gl2psDisable = _gl2ps.gl2psDisable

gl2psPointSize = _gl2ps.gl2psPointSize

gl2psLineWidth = _gl2ps.gl2psLineWidth

gl2psBlendFunc = _gl2ps.gl2psBlendFunc

gl2psDrawImageMap = _gl2ps.gl2psDrawImageMap

