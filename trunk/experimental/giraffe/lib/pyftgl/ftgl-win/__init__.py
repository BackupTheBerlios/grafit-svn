# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _ftgl

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


class FTFace(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, FTFace, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, FTFace, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ FTFace instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FTFace, 'this', _ftgl.new_FTFace(*args))
        _swig_setattr(self, FTFace, 'thisown', 1)
    def __del__(self, destroy=_ftgl.delete_FTFace):
        try:
            if self.thisown: destroy(self)
        except: pass

    def Attach(*args): return _ftgl.FTFace_Attach(*args)
    def Face(*args): return _ftgl.FTFace_Face(*args)
    def Size(*args): return _ftgl.FTFace_Size(*args)
    def CharMapCount(*args): return _ftgl.FTFace_CharMapCount(*args)
    def CharMapList(*args): return _ftgl.FTFace_CharMapList(*args)
    def KernAdvance(*args): return _ftgl.FTFace_KernAdvance(*args)
    def Glyph(*args): return _ftgl.FTFace_Glyph(*args)
    def GlyphCount(*args): return _ftgl.FTFace_GlyphCount(*args)
    def Error(*args): return _ftgl.FTFace_Error(*args)

class FTFacePtr(FTFace):
    def __init__(self, this):
        _swig_setattr(self, FTFace, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FTFace, 'thisown', 0)
        _swig_setattr(self, FTFace,self.__class__,FTFace)
_ftgl.FTFace_swigregister(FTFacePtr)

class FTFont(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, FTFont, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, FTFont, name)
    def __init__(self): raise RuntimeError, "No constructor defined"
    def __repr__(self):
        return "<%s.%s; proxy of C++ FTFont instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __del__(self, destroy=_ftgl.delete_FTFont):
        try:
            if self.thisown: destroy(self)
        except: pass

    def Attach(*args): return _ftgl.FTFont_Attach(*args)
    def CharMap(*args): return _ftgl.FTFont_CharMap(*args)
    def CharMapCount(*args): return _ftgl.FTFont_CharMapCount(*args)
    def CharMapList(*args): return _ftgl.FTFont_CharMapList(*args)
    def FaceSize(*args): return _ftgl.FTFont_FaceSize(*args)
    def Depth(*args): return _ftgl.FTFont_Depth(*args)
    def UseDisplayList(*args): return _ftgl.FTFont_UseDisplayList(*args)
    def Ascender(*args): return _ftgl.FTFont_Ascender(*args)
    def Descender(*args): return _ftgl.FTFont_Descender(*args)
    def LineHeight(*args): return _ftgl.FTFont_LineHeight(*args)
    def BBox(*args): return _ftgl.FTFont_BBox(*args)
    def Advance(*args): return _ftgl.FTFont_Advance(*args)
    def Render(*args): return _ftgl.FTFont_Render(*args)
    def Error(*args): return _ftgl.FTFont_Error(*args)

class FTFontPtr(FTFont):
    def __init__(self, this):
        _swig_setattr(self, FTFont, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FTFont, 'thisown', 0)
        _swig_setattr(self, FTFont,self.__class__,FTFont)
_ftgl.FTFont_swigregister(FTFontPtr)

class FTGLOutlineFont(FTFont):
    __swig_setmethods__ = {}
    for _s in [FTFont]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FTGLOutlineFont, name, value)
    __swig_getmethods__ = {}
    for _s in [FTFont]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FTGLOutlineFont, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ FTGLOutlineFont instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FTGLOutlineFont, 'this', _ftgl.new_FTGLOutlineFont(*args))
        _swig_setattr(self, FTGLOutlineFont, 'thisown', 1)
    def __del__(self, destroy=_ftgl.delete_FTGLOutlineFont):
        try:
            if self.thisown: destroy(self)
        except: pass

    def Render(*args): return _ftgl.FTGLOutlineFont_Render(*args)

class FTGLOutlineFontPtr(FTGLOutlineFont):
    def __init__(self, this):
        _swig_setattr(self, FTGLOutlineFont, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FTGLOutlineFont, 'thisown', 0)
        _swig_setattr(self, FTGLOutlineFont,self.__class__,FTGLOutlineFont)
_ftgl.FTGLOutlineFont_swigregister(FTGLOutlineFontPtr)

class FTGLPolygonFont(FTFont):
    __swig_setmethods__ = {}
    for _s in [FTFont]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FTGLPolygonFont, name, value)
    __swig_getmethods__ = {}
    for _s in [FTFont]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FTGLPolygonFont, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ FTGLPolygonFont instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FTGLPolygonFont, 'this', _ftgl.new_FTGLPolygonFont(*args))
        _swig_setattr(self, FTGLPolygonFont, 'thisown', 1)
    def __del__(self, destroy=_ftgl.delete_FTGLPolygonFont):
        try:
            if self.thisown: destroy(self)
        except: pass


class FTGLPolygonFontPtr(FTGLPolygonFont):
    def __init__(self, this):
        _swig_setattr(self, FTGLPolygonFont, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FTGLPolygonFont, 'thisown', 0)
        _swig_setattr(self, FTGLPolygonFont,self.__class__,FTGLPolygonFont)
_ftgl.FTGLPolygonFont_swigregister(FTGLPolygonFontPtr)

class FTGLTextureFont(FTFont):
    __swig_setmethods__ = {}
    for _s in [FTFont]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FTGLTextureFont, name, value)
    __swig_getmethods__ = {}
    for _s in [FTFont]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FTGLTextureFont, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ FTGLTextureFont instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FTGLTextureFont, 'this', _ftgl.new_FTGLTextureFont(*args))
        _swig_setattr(self, FTGLTextureFont, 'thisown', 1)
    def __del__(self, destroy=_ftgl.delete_FTGLTextureFont):
        try:
            if self.thisown: destroy(self)
        except: pass

    def FaceSize(*args): return _ftgl.FTGLTextureFont_FaceSize(*args)
    def Render(*args): return _ftgl.FTGLTextureFont_Render(*args)

class FTGLTextureFontPtr(FTGLTextureFont):
    def __init__(self, this):
        _swig_setattr(self, FTGLTextureFont, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FTGLTextureFont, 'thisown', 0)
        _swig_setattr(self, FTGLTextureFont,self.__class__,FTGLTextureFont)
_ftgl.FTGLTextureFont_swigregister(FTGLTextureFontPtr)

class FTGLBitmapFont(FTFont):
    __swig_setmethods__ = {}
    for _s in [FTFont]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FTGLBitmapFont, name, value)
    __swig_getmethods__ = {}
    for _s in [FTFont]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FTGLBitmapFont, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ FTGLBitmapFont instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FTGLBitmapFont, 'this', _ftgl.new_FTGLBitmapFont(*args))
        _swig_setattr(self, FTGLBitmapFont, 'thisown', 1)
    def __del__(self, destroy=_ftgl.delete_FTGLBitmapFont):
        try:
            if self.thisown: destroy(self)
        except: pass

    def Render(*args): return _ftgl.FTGLBitmapFont_Render(*args)

class FTGLBitmapFontPtr(FTGLBitmapFont):
    def __init__(self, this):
        _swig_setattr(self, FTGLBitmapFont, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FTGLBitmapFont, 'thisown', 0)
        _swig_setattr(self, FTGLBitmapFont,self.__class__,FTGLBitmapFont)
_ftgl.FTGLBitmapFont_swigregister(FTGLBitmapFontPtr)

class FTGLPixmapFont(FTFont):
    __swig_setmethods__ = {}
    for _s in [FTFont]: __swig_setmethods__.update(_s.__swig_setmethods__)
    __setattr__ = lambda self, name, value: _swig_setattr(self, FTGLPixmapFont, name, value)
    __swig_getmethods__ = {}
    for _s in [FTFont]: __swig_getmethods__.update(_s.__swig_getmethods__)
    __getattr__ = lambda self, name: _swig_getattr(self, FTGLPixmapFont, name)
    def __repr__(self):
        return "<%s.%s; proxy of C++ FTGLPixmapFont instance at %s>" % (self.__class__.__module__, self.__class__.__name__, self.this,)
    def __init__(self, *args):
        _swig_setattr(self, FTGLPixmapFont, 'this', _ftgl.new_FTGLPixmapFont(*args))
        _swig_setattr(self, FTGLPixmapFont, 'thisown', 1)
    def __del__(self, destroy=_ftgl.delete_FTGLPixmapFont):
        try:
            if self.thisown: destroy(self)
        except: pass

    def Render(*args): return _ftgl.FTGLPixmapFont_Render(*args)

class FTGLPixmapFontPtr(FTGLPixmapFont):
    def __init__(self, this):
        _swig_setattr(self, FTGLPixmapFont, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, FTGLPixmapFont, 'thisown', 0)
        _swig_setattr(self, FTGLPixmapFont,self.__class__,FTGLPixmapFont)
_ftgl.FTGLPixmapFont_swigregister(FTGLPixmapFontPtr)


