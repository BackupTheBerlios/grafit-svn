# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _gl2ps

def _swig_setattr(self,class_type,name,value):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    self.__dict__[name] = value

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
GL2PS_POLYGON_OFFSET_FILL = _gl2ps.GL2PS_POLYGON_OFFSET_FILL
GL2PS_POLYGON_BOUNDARY = _gl2ps.GL2PS_POLYGON_BOUNDARY
GL2PS_LINE_STIPPLE = _gl2ps.GL2PS_LINE_STIPPLE
GL2PS_EPSILON = _gl2ps.GL2PS_EPSILON
GL2PS_DEPTH_FACT = _gl2ps.GL2PS_DEPTH_FACT
GL2PS_SIMPLE_OFFSET = _gl2ps.GL2PS_SIMPLE_OFFSET
GL2PS_SIMPLE_OFFSET_LARGE = _gl2ps.GL2PS_SIMPLE_OFFSET_LARGE
GL2PS_FIXED_XREF_ENTRIES = _gl2ps.GL2PS_FIXED_XREF_ENTRIES
GL2PS_SUCCESS = _gl2ps.GL2PS_SUCCESS
GL2PS_INFO = _gl2ps.GL2PS_INFO
GL2PS_WARNING = _gl2ps.GL2PS_WARNING
GL2PS_ERROR = _gl2ps.GL2PS_ERROR
GL2PS_NO_FEEDBACK = _gl2ps.GL2PS_NO_FEEDBACK
GL2PS_OVERFLOW = _gl2ps.GL2PS_OVERFLOW
GL2PS_UNINITIALIZED = _gl2ps.GL2PS_UNINITIALIZED
GL2PS_NOTYPE = _gl2ps.GL2PS_NOTYPE
GL2PS_TEXT = _gl2ps.GL2PS_TEXT
GL2PS_POINT = _gl2ps.GL2PS_POINT
GL2PS_LINE = _gl2ps.GL2PS_LINE
GL2PS_QUADRANGLE = _gl2ps.GL2PS_QUADRANGLE
GL2PS_TRIANGLE = _gl2ps.GL2PS_TRIANGLE
GL2PS_PIXMAP = _gl2ps.GL2PS_PIXMAP
GL2PS_TEXT_C = _gl2ps.GL2PS_TEXT_C
GL2PS_TEXT_CL = _gl2ps.GL2PS_TEXT_CL
GL2PS_TEXT_CR = _gl2ps.GL2PS_TEXT_CR
GL2PS_TEXT_B = _gl2ps.GL2PS_TEXT_B
GL2PS_TEXT_BL = _gl2ps.GL2PS_TEXT_BL
GL2PS_TEXT_BR = _gl2ps.GL2PS_TEXT_BR
GL2PS_TEXT_T = _gl2ps.GL2PS_TEXT_T
GL2PS_TEXT_TL = _gl2ps.GL2PS_TEXT_TL
GL2PS_TEXT_TR = _gl2ps.GL2PS_TEXT_TR
GL2PS_COINCIDENT = _gl2ps.GL2PS_COINCIDENT
GL2PS_IN_FRONT_OF = _gl2ps.GL2PS_IN_FRONT_OF
GL2PS_IN_BACK_OF = _gl2ps.GL2PS_IN_BACK_OF
GL2PS_SPANNING = _gl2ps.GL2PS_SPANNING
GL2PS_POINT_COINCIDENT = _gl2ps.GL2PS_POINT_COINCIDENT
GL2PS_POINT_INFRONT = _gl2ps.GL2PS_POINT_INFRONT
GL2PS_POINT_BACK = _gl2ps.GL2PS_POINT_BACK
GL2PS_BEGIN_POLYGON_OFFSET_FILL = _gl2ps.GL2PS_BEGIN_POLYGON_OFFSET_FILL
GL2PS_END_POLYGON_OFFSET_FILL = _gl2ps.GL2PS_END_POLYGON_OFFSET_FILL
GL2PS_BEGIN_POLYGON_BOUNDARY = _gl2ps.GL2PS_BEGIN_POLYGON_BOUNDARY
GL2PS_END_POLYGON_BOUNDARY = _gl2ps.GL2PS_END_POLYGON_BOUNDARY
GL2PS_BEGIN_LINE_STIPPLE = _gl2ps.GL2PS_BEGIN_LINE_STIPPLE
GL2PS_END_LINE_STIPPLE = _gl2ps.GL2PS_END_LINE_STIPPLE
GL2PS_SET_POINT_SIZE = _gl2ps.GL2PS_SET_POINT_SIZE
GL2PS_SET_LINE_WIDTH = _gl2ps.GL2PS_SET_LINE_WIDTH
class _GL2PSbsptree2d(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, _GL2PSbsptree2d, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, _GL2PSbsptree2d, name)
    def __repr__(self):
        return "<C _GL2PSbsptree2d instance at %s>" % (self.this,)
    __swig_setmethods__["plane"] = _gl2ps._GL2PSbsptree2d_plane_set
    __swig_getmethods__["plane"] = _gl2ps._GL2PSbsptree2d_plane_get
    if _newclass:plane = property(_gl2ps._GL2PSbsptree2d_plane_get, _gl2ps._GL2PSbsptree2d_plane_set)
    __swig_setmethods__["front"] = _gl2ps._GL2PSbsptree2d_front_set
    __swig_getmethods__["front"] = _gl2ps._GL2PSbsptree2d_front_get
    if _newclass:front = property(_gl2ps._GL2PSbsptree2d_front_get, _gl2ps._GL2PSbsptree2d_front_set)
    __swig_setmethods__["back"] = _gl2ps._GL2PSbsptree2d_back_set
    __swig_getmethods__["back"] = _gl2ps._GL2PSbsptree2d_back_get
    if _newclass:back = property(_gl2ps._GL2PSbsptree2d_back_get, _gl2ps._GL2PSbsptree2d_back_set)
    def __init__(self, *args):
        _swig_setattr(self, _GL2PSbsptree2d, 'this', _gl2ps.new__GL2PSbsptree2d(*args))
        _swig_setattr(self, _GL2PSbsptree2d, 'thisown', 1)
    def __del__(self, destroy=_gl2ps.delete__GL2PSbsptree2d):
        try:
            if self.thisown: destroy(self)
        except: pass

class _GL2PSbsptree2dPtr(_GL2PSbsptree2d):
    def __init__(self, this):
        _swig_setattr(self, _GL2PSbsptree2d, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, _GL2PSbsptree2d, 'thisown', 0)
        _swig_setattr(self, _GL2PSbsptree2d,self.__class__,_GL2PSbsptree2d)
_gl2ps._GL2PSbsptree2d_swigregister(_GL2PSbsptree2dPtr)

class GL2PSlist(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, GL2PSlist, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, GL2PSlist, name)
    def __repr__(self):
        return "<C GL2PSlist instance at %s>" % (self.this,)
    __swig_setmethods__["nmax"] = _gl2ps.GL2PSlist_nmax_set
    __swig_getmethods__["nmax"] = _gl2ps.GL2PSlist_nmax_get
    if _newclass:nmax = property(_gl2ps.GL2PSlist_nmax_get, _gl2ps.GL2PSlist_nmax_set)
    __swig_setmethods__["size"] = _gl2ps.GL2PSlist_size_set
    __swig_getmethods__["size"] = _gl2ps.GL2PSlist_size_get
    if _newclass:size = property(_gl2ps.GL2PSlist_size_get, _gl2ps.GL2PSlist_size_set)
    __swig_setmethods__["incr"] = _gl2ps.GL2PSlist_incr_set
    __swig_getmethods__["incr"] = _gl2ps.GL2PSlist_incr_get
    if _newclass:incr = property(_gl2ps.GL2PSlist_incr_get, _gl2ps.GL2PSlist_incr_set)
    __swig_setmethods__["n"] = _gl2ps.GL2PSlist_n_set
    __swig_getmethods__["n"] = _gl2ps.GL2PSlist_n_get
    if _newclass:n = property(_gl2ps.GL2PSlist_n_get, _gl2ps.GL2PSlist_n_set)
    __swig_setmethods__["array"] = _gl2ps.GL2PSlist_array_set
    __swig_getmethods__["array"] = _gl2ps.GL2PSlist_array_get
    if _newclass:array = property(_gl2ps.GL2PSlist_array_get, _gl2ps.GL2PSlist_array_set)
    def __init__(self, *args):
        _swig_setattr(self, GL2PSlist, 'this', _gl2ps.new_GL2PSlist(*args))
        _swig_setattr(self, GL2PSlist, 'thisown', 1)
    def __del__(self, destroy=_gl2ps.delete_GL2PSlist):
        try:
            if self.thisown: destroy(self)
        except: pass

class GL2PSlistPtr(GL2PSlist):
    def __init__(self, this):
        _swig_setattr(self, GL2PSlist, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, GL2PSlist, 'thisown', 0)
        _swig_setattr(self, GL2PSlist,self.__class__,GL2PSlist)
_gl2ps.GL2PSlist_swigregister(GL2PSlistPtr)

class _GL2PSbsptree(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, _GL2PSbsptree, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, _GL2PSbsptree, name)
    def __repr__(self):
        return "<C _GL2PSbsptree instance at %s>" % (self.this,)
    __swig_setmethods__["plane"] = _gl2ps._GL2PSbsptree_plane_set
    __swig_getmethods__["plane"] = _gl2ps._GL2PSbsptree_plane_get
    if _newclass:plane = property(_gl2ps._GL2PSbsptree_plane_get, _gl2ps._GL2PSbsptree_plane_set)
    __swig_setmethods__["primitives"] = _gl2ps._GL2PSbsptree_primitives_set
    __swig_getmethods__["primitives"] = _gl2ps._GL2PSbsptree_primitives_get
    if _newclass:primitives = property(_gl2ps._GL2PSbsptree_primitives_get, _gl2ps._GL2PSbsptree_primitives_set)
    __swig_setmethods__["front"] = _gl2ps._GL2PSbsptree_front_set
    __swig_getmethods__["front"] = _gl2ps._GL2PSbsptree_front_get
    if _newclass:front = property(_gl2ps._GL2PSbsptree_front_get, _gl2ps._GL2PSbsptree_front_set)
    __swig_setmethods__["back"] = _gl2ps._GL2PSbsptree_back_set
    __swig_getmethods__["back"] = _gl2ps._GL2PSbsptree_back_get
    if _newclass:back = property(_gl2ps._GL2PSbsptree_back_get, _gl2ps._GL2PSbsptree_back_set)
    def __init__(self, *args):
        _swig_setattr(self, _GL2PSbsptree, 'this', _gl2ps.new__GL2PSbsptree(*args))
        _swig_setattr(self, _GL2PSbsptree, 'thisown', 1)
    def __del__(self, destroy=_gl2ps.delete__GL2PSbsptree):
        try:
            if self.thisown: destroy(self)
        except: pass

class _GL2PSbsptreePtr(_GL2PSbsptree):
    def __init__(self, this):
        _swig_setattr(self, _GL2PSbsptree, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, _GL2PSbsptree, 'thisown', 0)
        _swig_setattr(self, _GL2PSbsptree,self.__class__,_GL2PSbsptree)
_gl2ps._GL2PSbsptree_swigregister(_GL2PSbsptreePtr)

class GL2PSvertex(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, GL2PSvertex, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, GL2PSvertex, name)
    def __repr__(self):
        return "<C GL2PSvertex instance at %s>" % (self.this,)
    __swig_setmethods__["xyz"] = _gl2ps.GL2PSvertex_xyz_set
    __swig_getmethods__["xyz"] = _gl2ps.GL2PSvertex_xyz_get
    if _newclass:xyz = property(_gl2ps.GL2PSvertex_xyz_get, _gl2ps.GL2PSvertex_xyz_set)
    __swig_setmethods__["rgba"] = _gl2ps.GL2PSvertex_rgba_set
    __swig_getmethods__["rgba"] = _gl2ps.GL2PSvertex_rgba_get
    if _newclass:rgba = property(_gl2ps.GL2PSvertex_rgba_get, _gl2ps.GL2PSvertex_rgba_set)
    def __init__(self, *args):
        _swig_setattr(self, GL2PSvertex, 'this', _gl2ps.new_GL2PSvertex(*args))
        _swig_setattr(self, GL2PSvertex, 'thisown', 1)
    def __del__(self, destroy=_gl2ps.delete_GL2PSvertex):
        try:
            if self.thisown: destroy(self)
        except: pass

class GL2PSvertexPtr(GL2PSvertex):
    def __init__(self, this):
        _swig_setattr(self, GL2PSvertex, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, GL2PSvertex, 'thisown', 0)
        _swig_setattr(self, GL2PSvertex,self.__class__,GL2PSvertex)
_gl2ps.GL2PSvertex_swigregister(GL2PSvertexPtr)

class GL2PSstring(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, GL2PSstring, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, GL2PSstring, name)
    def __repr__(self):
        return "<C GL2PSstring instance at %s>" % (self.this,)
    __swig_setmethods__["fontsize"] = _gl2ps.GL2PSstring_fontsize_set
    __swig_getmethods__["fontsize"] = _gl2ps.GL2PSstring_fontsize_get
    if _newclass:fontsize = property(_gl2ps.GL2PSstring_fontsize_get, _gl2ps.GL2PSstring_fontsize_set)
    __swig_setmethods__["str"] = _gl2ps.GL2PSstring_str_set
    __swig_getmethods__["str"] = _gl2ps.GL2PSstring_str_get
    if _newclass:str = property(_gl2ps.GL2PSstring_str_get, _gl2ps.GL2PSstring_str_set)
    __swig_setmethods__["fontname"] = _gl2ps.GL2PSstring_fontname_set
    __swig_getmethods__["fontname"] = _gl2ps.GL2PSstring_fontname_get
    if _newclass:fontname = property(_gl2ps.GL2PSstring_fontname_get, _gl2ps.GL2PSstring_fontname_set)
    __swig_setmethods__["alignment"] = _gl2ps.GL2PSstring_alignment_set
    __swig_getmethods__["alignment"] = _gl2ps.GL2PSstring_alignment_get
    if _newclass:alignment = property(_gl2ps.GL2PSstring_alignment_get, _gl2ps.GL2PSstring_alignment_set)
    def __init__(self, *args):
        _swig_setattr(self, GL2PSstring, 'this', _gl2ps.new_GL2PSstring(*args))
        _swig_setattr(self, GL2PSstring, 'thisown', 1)
    def __del__(self, destroy=_gl2ps.delete_GL2PSstring):
        try:
            if self.thisown: destroy(self)
        except: pass

class GL2PSstringPtr(GL2PSstring):
    def __init__(self, this):
        _swig_setattr(self, GL2PSstring, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, GL2PSstring, 'thisown', 0)
        _swig_setattr(self, GL2PSstring,self.__class__,GL2PSstring)
_gl2ps.GL2PSstring_swigregister(GL2PSstringPtr)

class GL2PSimage(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, GL2PSimage, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, GL2PSimage, name)
    def __repr__(self):
        return "<C GL2PSimage instance at %s>" % (self.this,)
    __swig_setmethods__["width"] = _gl2ps.GL2PSimage_width_set
    __swig_getmethods__["width"] = _gl2ps.GL2PSimage_width_get
    if _newclass:width = property(_gl2ps.GL2PSimage_width_get, _gl2ps.GL2PSimage_width_set)
    __swig_setmethods__["height"] = _gl2ps.GL2PSimage_height_set
    __swig_getmethods__["height"] = _gl2ps.GL2PSimage_height_get
    if _newclass:height = property(_gl2ps.GL2PSimage_height_get, _gl2ps.GL2PSimage_height_set)
    __swig_setmethods__["format"] = _gl2ps.GL2PSimage_format_set
    __swig_getmethods__["format"] = _gl2ps.GL2PSimage_format_get
    if _newclass:format = property(_gl2ps.GL2PSimage_format_get, _gl2ps.GL2PSimage_format_set)
    __swig_setmethods__["type"] = _gl2ps.GL2PSimage_type_set
    __swig_getmethods__["type"] = _gl2ps.GL2PSimage_type_get
    if _newclass:type = property(_gl2ps.GL2PSimage_type_get, _gl2ps.GL2PSimage_type_set)
    __swig_setmethods__["pixels"] = _gl2ps.GL2PSimage_pixels_set
    __swig_getmethods__["pixels"] = _gl2ps.GL2PSimage_pixels_get
    if _newclass:pixels = property(_gl2ps.GL2PSimage_pixels_get, _gl2ps.GL2PSimage_pixels_set)
    def __init__(self, *args):
        _swig_setattr(self, GL2PSimage, 'this', _gl2ps.new_GL2PSimage(*args))
        _swig_setattr(self, GL2PSimage, 'thisown', 1)
    def __del__(self, destroy=_gl2ps.delete_GL2PSimage):
        try:
            if self.thisown: destroy(self)
        except: pass

class GL2PSimagePtr(GL2PSimage):
    def __init__(self, this):
        _swig_setattr(self, GL2PSimage, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, GL2PSimage, 'thisown', 0)
        _swig_setattr(self, GL2PSimage,self.__class__,GL2PSimage)
_gl2ps.GL2PSimage_swigregister(GL2PSimagePtr)

class GL2PSprimitive(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, GL2PSprimitive, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, GL2PSprimitive, name)
    def __repr__(self):
        return "<C GL2PSprimitive instance at %s>" % (self.this,)
    __swig_setmethods__["type"] = _gl2ps.GL2PSprimitive_type_set
    __swig_getmethods__["type"] = _gl2ps.GL2PSprimitive_type_get
    if _newclass:type = property(_gl2ps.GL2PSprimitive_type_get, _gl2ps.GL2PSprimitive_type_set)
    __swig_setmethods__["numverts"] = _gl2ps.GL2PSprimitive_numverts_set
    __swig_getmethods__["numverts"] = _gl2ps.GL2PSprimitive_numverts_get
    if _newclass:numverts = property(_gl2ps.GL2PSprimitive_numverts_get, _gl2ps.GL2PSprimitive_numverts_set)
    __swig_setmethods__["boundary"] = _gl2ps.GL2PSprimitive_boundary_set
    __swig_getmethods__["boundary"] = _gl2ps.GL2PSprimitive_boundary_get
    if _newclass:boundary = property(_gl2ps.GL2PSprimitive_boundary_get, _gl2ps.GL2PSprimitive_boundary_set)
    __swig_setmethods__["dash"] = _gl2ps.GL2PSprimitive_dash_set
    __swig_getmethods__["dash"] = _gl2ps.GL2PSprimitive_dash_get
    if _newclass:dash = property(_gl2ps.GL2PSprimitive_dash_get, _gl2ps.GL2PSprimitive_dash_set)
    __swig_setmethods__["culled"] = _gl2ps.GL2PSprimitive_culled_set
    __swig_getmethods__["culled"] = _gl2ps.GL2PSprimitive_culled_get
    if _newclass:culled = property(_gl2ps.GL2PSprimitive_culled_get, _gl2ps.GL2PSprimitive_culled_set)
    __swig_setmethods__["width"] = _gl2ps.GL2PSprimitive_width_set
    __swig_getmethods__["width"] = _gl2ps.GL2PSprimitive_width_get
    if _newclass:width = property(_gl2ps.GL2PSprimitive_width_get, _gl2ps.GL2PSprimitive_width_set)
    __swig_setmethods__["depth"] = _gl2ps.GL2PSprimitive_depth_set
    __swig_getmethods__["depth"] = _gl2ps.GL2PSprimitive_depth_get
    if _newclass:depth = property(_gl2ps.GL2PSprimitive_depth_get, _gl2ps.GL2PSprimitive_depth_set)
    __swig_setmethods__["verts"] = _gl2ps.GL2PSprimitive_verts_set
    __swig_getmethods__["verts"] = _gl2ps.GL2PSprimitive_verts_get
    if _newclass:verts = property(_gl2ps.GL2PSprimitive_verts_get, _gl2ps.GL2PSprimitive_verts_set)
    __swig_getmethods__["data"] = _gl2ps.GL2PSprimitive_data_get
    if _newclass:data = property(_gl2ps.GL2PSprimitive_data_get)
    def __init__(self, *args):
        _swig_setattr(self, GL2PSprimitive, 'this', _gl2ps.new_GL2PSprimitive(*args))
        _swig_setattr(self, GL2PSprimitive, 'thisown', 1)
    def __del__(self, destroy=_gl2ps.delete_GL2PSprimitive):
        try:
            if self.thisown: destroy(self)
        except: pass

class GL2PSprimitivePtr(GL2PSprimitive):
    def __init__(self, this):
        _swig_setattr(self, GL2PSprimitive, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, GL2PSprimitive, 'thisown', 0)
        _swig_setattr(self, GL2PSprimitive,self.__class__,GL2PSprimitive)
_gl2ps.GL2PSprimitive_swigregister(GL2PSprimitivePtr)

class GL2PSprimitive_data(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, GL2PSprimitive_data, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, GL2PSprimitive_data, name)
    def __repr__(self):
        return "<C GL2PSprimitive_data instance at %s>" % (self.this,)
    __swig_setmethods__["text"] = _gl2ps.GL2PSprimitive_data_text_set
    __swig_getmethods__["text"] = _gl2ps.GL2PSprimitive_data_text_get
    if _newclass:text = property(_gl2ps.GL2PSprimitive_data_text_get, _gl2ps.GL2PSprimitive_data_text_set)
    __swig_setmethods__["image"] = _gl2ps.GL2PSprimitive_data_image_set
    __swig_getmethods__["image"] = _gl2ps.GL2PSprimitive_data_image_get
    if _newclass:image = property(_gl2ps.GL2PSprimitive_data_image_get, _gl2ps.GL2PSprimitive_data_image_set)
    def __init__(self, *args):
        _swig_setattr(self, GL2PSprimitive_data, 'this', _gl2ps.new_GL2PSprimitive_data(*args))
        _swig_setattr(self, GL2PSprimitive_data, 'thisown', 1)
    def __del__(self, destroy=_gl2ps.delete_GL2PSprimitive_data):
        try:
            if self.thisown: destroy(self)
        except: pass

class GL2PSprimitive_dataPtr(GL2PSprimitive_data):
    def __init__(self, this):
        _swig_setattr(self, GL2PSprimitive_data, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, GL2PSprimitive_data, 'thisown', 0)
        _swig_setattr(self, GL2PSprimitive_data,self.__class__,GL2PSprimitive_data)
_gl2ps.GL2PSprimitive_data_swigregister(GL2PSprimitive_dataPtr)

class GL2PScompress(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, GL2PScompress, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, GL2PScompress, name)
    def __repr__(self):
        return "<C GL2PScompress instance at %s>" % (self.this,)
    __swig_setmethods__["dummy"] = _gl2ps.GL2PScompress_dummy_set
    __swig_getmethods__["dummy"] = _gl2ps.GL2PScompress_dummy_get
    if _newclass:dummy = property(_gl2ps.GL2PScompress_dummy_get, _gl2ps.GL2PScompress_dummy_set)
    def __init__(self, *args):
        _swig_setattr(self, GL2PScompress, 'this', _gl2ps.new_GL2PScompress(*args))
        _swig_setattr(self, GL2PScompress, 'thisown', 1)
    def __del__(self, destroy=_gl2ps.delete_GL2PScompress):
        try:
            if self.thisown: destroy(self)
        except: pass

class GL2PScompressPtr(GL2PScompress):
    def __init__(self, this):
        _swig_setattr(self, GL2PScompress, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, GL2PScompress, 'thisown', 0)
        _swig_setattr(self, GL2PScompress,self.__class__,GL2PScompress)
_gl2ps.GL2PScompress_swigregister(GL2PScompressPtr)

class GL2PScontext(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, GL2PScontext, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, GL2PScontext, name)
    def __repr__(self):
        return "<C GL2PScontext instance at %s>" % (self.this,)
    __swig_setmethods__["format"] = _gl2ps.GL2PScontext_format_set
    __swig_getmethods__["format"] = _gl2ps.GL2PScontext_format_get
    if _newclass:format = property(_gl2ps.GL2PScontext_format_get, _gl2ps.GL2PScontext_format_set)
    __swig_setmethods__["sort"] = _gl2ps.GL2PScontext_sort_set
    __swig_getmethods__["sort"] = _gl2ps.GL2PScontext_sort_get
    if _newclass:sort = property(_gl2ps.GL2PScontext_sort_get, _gl2ps.GL2PScontext_sort_set)
    __swig_setmethods__["options"] = _gl2ps.GL2PScontext_options_set
    __swig_getmethods__["options"] = _gl2ps.GL2PScontext_options_get
    if _newclass:options = property(_gl2ps.GL2PScontext_options_get, _gl2ps.GL2PScontext_options_set)
    __swig_setmethods__["colorsize"] = _gl2ps.GL2PScontext_colorsize_set
    __swig_getmethods__["colorsize"] = _gl2ps.GL2PScontext_colorsize_get
    if _newclass:colorsize = property(_gl2ps.GL2PScontext_colorsize_get, _gl2ps.GL2PScontext_colorsize_set)
    __swig_setmethods__["colormode"] = _gl2ps.GL2PScontext_colormode_set
    __swig_getmethods__["colormode"] = _gl2ps.GL2PScontext_colormode_get
    if _newclass:colormode = property(_gl2ps.GL2PScontext_colormode_get, _gl2ps.GL2PScontext_colormode_set)
    __swig_setmethods__["buffersize"] = _gl2ps.GL2PScontext_buffersize_set
    __swig_getmethods__["buffersize"] = _gl2ps.GL2PScontext_buffersize_get
    if _newclass:buffersize = property(_gl2ps.GL2PScontext_buffersize_get, _gl2ps.GL2PScontext_buffersize_set)
    __swig_setmethods__["title"] = _gl2ps.GL2PScontext_title_set
    __swig_getmethods__["title"] = _gl2ps.GL2PScontext_title_get
    if _newclass:title = property(_gl2ps.GL2PScontext_title_get, _gl2ps.GL2PScontext_title_set)
    __swig_setmethods__["producer"] = _gl2ps.GL2PScontext_producer_set
    __swig_getmethods__["producer"] = _gl2ps.GL2PScontext_producer_get
    if _newclass:producer = property(_gl2ps.GL2PScontext_producer_get, _gl2ps.GL2PScontext_producer_set)
    __swig_setmethods__["filename"] = _gl2ps.GL2PScontext_filename_set
    __swig_getmethods__["filename"] = _gl2ps.GL2PScontext_filename_get
    if _newclass:filename = property(_gl2ps.GL2PScontext_filename_get, _gl2ps.GL2PScontext_filename_set)
    __swig_setmethods__["boundary"] = _gl2ps.GL2PScontext_boundary_set
    __swig_getmethods__["boundary"] = _gl2ps.GL2PScontext_boundary_get
    if _newclass:boundary = property(_gl2ps.GL2PScontext_boundary_get, _gl2ps.GL2PScontext_boundary_set)
    __swig_setmethods__["feedback"] = _gl2ps.GL2PScontext_feedback_set
    __swig_getmethods__["feedback"] = _gl2ps.GL2PScontext_feedback_get
    if _newclass:feedback = property(_gl2ps.GL2PScontext_feedback_get, _gl2ps.GL2PScontext_feedback_set)
    __swig_setmethods__["offset"] = _gl2ps.GL2PScontext_offset_set
    __swig_getmethods__["offset"] = _gl2ps.GL2PScontext_offset_get
    if _newclass:offset = property(_gl2ps.GL2PScontext_offset_get, _gl2ps.GL2PScontext_offset_set)
    __swig_setmethods__["lastlinewidth"] = _gl2ps.GL2PScontext_lastlinewidth_set
    __swig_getmethods__["lastlinewidth"] = _gl2ps.GL2PScontext_lastlinewidth_get
    if _newclass:lastlinewidth = property(_gl2ps.GL2PScontext_lastlinewidth_get, _gl2ps.GL2PScontext_lastlinewidth_set)
    __swig_setmethods__["viewport"] = _gl2ps.GL2PScontext_viewport_set
    __swig_getmethods__["viewport"] = _gl2ps.GL2PScontext_viewport_get
    if _newclass:viewport = property(_gl2ps.GL2PScontext_viewport_get, _gl2ps.GL2PScontext_viewport_set)
    __swig_setmethods__["colormap"] = _gl2ps.GL2PScontext_colormap_set
    __swig_getmethods__["colormap"] = _gl2ps.GL2PScontext_colormap_get
    if _newclass:colormap = property(_gl2ps.GL2PScontext_colormap_get, _gl2ps.GL2PScontext_colormap_set)
    __swig_setmethods__["lastrgba"] = _gl2ps.GL2PScontext_lastrgba_set
    __swig_getmethods__["lastrgba"] = _gl2ps.GL2PScontext_lastrgba_get
    if _newclass:lastrgba = property(_gl2ps.GL2PScontext_lastrgba_get, _gl2ps.GL2PScontext_lastrgba_set)
    __swig_setmethods__["threshold"] = _gl2ps.GL2PScontext_threshold_set
    __swig_getmethods__["threshold"] = _gl2ps.GL2PScontext_threshold_get
    if _newclass:threshold = property(_gl2ps.GL2PScontext_threshold_get, _gl2ps.GL2PScontext_threshold_set)
    __swig_setmethods__["primitives"] = _gl2ps.GL2PScontext_primitives_set
    __swig_getmethods__["primitives"] = _gl2ps.GL2PScontext_primitives_get
    if _newclass:primitives = property(_gl2ps.GL2PScontext_primitives_get, _gl2ps.GL2PScontext_primitives_set)
    __swig_setmethods__["stream"] = _gl2ps.GL2PScontext_stream_set
    __swig_getmethods__["stream"] = _gl2ps.GL2PScontext_stream_get
    if _newclass:stream = property(_gl2ps.GL2PScontext_stream_get, _gl2ps.GL2PScontext_stream_set)
    __swig_setmethods__["compress"] = _gl2ps.GL2PScontext_compress_set
    __swig_getmethods__["compress"] = _gl2ps.GL2PScontext_compress_get
    if _newclass:compress = property(_gl2ps.GL2PScontext_compress_get, _gl2ps.GL2PScontext_compress_set)
    __swig_setmethods__["maxbestroot"] = _gl2ps.GL2PScontext_maxbestroot_set
    __swig_getmethods__["maxbestroot"] = _gl2ps.GL2PScontext_maxbestroot_get
    if _newclass:maxbestroot = property(_gl2ps.GL2PScontext_maxbestroot_get, _gl2ps.GL2PScontext_maxbestroot_set)
    __swig_setmethods__["zerosurfacearea"] = _gl2ps.GL2PScontext_zerosurfacearea_set
    __swig_getmethods__["zerosurfacearea"] = _gl2ps.GL2PScontext_zerosurfacearea_get
    if _newclass:zerosurfacearea = property(_gl2ps.GL2PScontext_zerosurfacearea_get, _gl2ps.GL2PScontext_zerosurfacearea_set)
    __swig_setmethods__["imagetree"] = _gl2ps.GL2PScontext_imagetree_set
    __swig_getmethods__["imagetree"] = _gl2ps.GL2PScontext_imagetree_get
    if _newclass:imagetree = property(_gl2ps.GL2PScontext_imagetree_get, _gl2ps.GL2PScontext_imagetree_set)
    __swig_setmethods__["primitivetoadd"] = _gl2ps.GL2PScontext_primitivetoadd_set
    __swig_getmethods__["primitivetoadd"] = _gl2ps.GL2PScontext_primitivetoadd_get
    if _newclass:primitivetoadd = property(_gl2ps.GL2PScontext_primitivetoadd_get, _gl2ps.GL2PScontext_primitivetoadd_set)
    __swig_setmethods__["cref"] = _gl2ps.GL2PScontext_cref_set
    __swig_getmethods__["cref"] = _gl2ps.GL2PScontext_cref_get
    if _newclass:cref = property(_gl2ps.GL2PScontext_cref_get, _gl2ps.GL2PScontext_cref_set)
    __swig_setmethods__["streamlength"] = _gl2ps.GL2PScontext_streamlength_set
    __swig_getmethods__["streamlength"] = _gl2ps.GL2PScontext_streamlength_get
    if _newclass:streamlength = property(_gl2ps.GL2PScontext_streamlength_get, _gl2ps.GL2PScontext_streamlength_set)
    __swig_setmethods__["tlist"] = _gl2ps.GL2PScontext_tlist_set
    __swig_getmethods__["tlist"] = _gl2ps.GL2PScontext_tlist_get
    if _newclass:tlist = property(_gl2ps.GL2PScontext_tlist_get, _gl2ps.GL2PScontext_tlist_set)
    __swig_setmethods__["tidxlist"] = _gl2ps.GL2PScontext_tidxlist_set
    __swig_getmethods__["tidxlist"] = _gl2ps.GL2PScontext_tidxlist_get
    if _newclass:tidxlist = property(_gl2ps.GL2PScontext_tidxlist_get, _gl2ps.GL2PScontext_tidxlist_set)
    __swig_setmethods__["ilist"] = _gl2ps.GL2PScontext_ilist_set
    __swig_getmethods__["ilist"] = _gl2ps.GL2PScontext_ilist_get
    if _newclass:ilist = property(_gl2ps.GL2PScontext_ilist_get, _gl2ps.GL2PScontext_ilist_set)
    __swig_setmethods__["slist"] = _gl2ps.GL2PScontext_slist_set
    __swig_getmethods__["slist"] = _gl2ps.GL2PScontext_slist_get
    if _newclass:slist = property(_gl2ps.GL2PScontext_slist_get, _gl2ps.GL2PScontext_slist_set)
    __swig_setmethods__["lasttype"] = _gl2ps.GL2PScontext_lasttype_set
    __swig_getmethods__["lasttype"] = _gl2ps.GL2PScontext_lasttype_get
    if _newclass:lasttype = property(_gl2ps.GL2PScontext_lasttype_get, _gl2ps.GL2PScontext_lasttype_set)
    __swig_setmethods__["consec_cnt"] = _gl2ps.GL2PScontext_consec_cnt_set
    __swig_getmethods__["consec_cnt"] = _gl2ps.GL2PScontext_consec_cnt_get
    if _newclass:consec_cnt = property(_gl2ps.GL2PScontext_consec_cnt_get, _gl2ps.GL2PScontext_consec_cnt_set)
    __swig_setmethods__["consec_inner_cnt"] = _gl2ps.GL2PScontext_consec_inner_cnt_set
    __swig_getmethods__["consec_inner_cnt"] = _gl2ps.GL2PScontext_consec_inner_cnt_get
    if _newclass:consec_inner_cnt = property(_gl2ps.GL2PScontext_consec_inner_cnt_get, _gl2ps.GL2PScontext_consec_inner_cnt_set)
    __swig_setmethods__["line_width_diff"] = _gl2ps.GL2PScontext_line_width_diff_set
    __swig_getmethods__["line_width_diff"] = _gl2ps.GL2PScontext_line_width_diff_get
    if _newclass:line_width_diff = property(_gl2ps.GL2PScontext_line_width_diff_get, _gl2ps.GL2PScontext_line_width_diff_set)
    __swig_setmethods__["line_rgb_diff"] = _gl2ps.GL2PScontext_line_rgb_diff_set
    __swig_getmethods__["line_rgb_diff"] = _gl2ps.GL2PScontext_line_rgb_diff_get
    if _newclass:line_rgb_diff = property(_gl2ps.GL2PScontext_line_rgb_diff_get, _gl2ps.GL2PScontext_line_rgb_diff_set)
    __swig_setmethods__["last_line_finished"] = _gl2ps.GL2PScontext_last_line_finished_set
    __swig_getmethods__["last_line_finished"] = _gl2ps.GL2PScontext_last_line_finished_get
    if _newclass:last_line_finished = property(_gl2ps.GL2PScontext_last_line_finished_get, _gl2ps.GL2PScontext_last_line_finished_set)
    __swig_setmethods__["last_triangle_finished"] = _gl2ps.GL2PScontext_last_triangle_finished_set
    __swig_getmethods__["last_triangle_finished"] = _gl2ps.GL2PScontext_last_triangle_finished_get
    if _newclass:last_triangle_finished = property(_gl2ps.GL2PScontext_last_triangle_finished_get, _gl2ps.GL2PScontext_last_triangle_finished_set)
    def __init__(self, *args):
        _swig_setattr(self, GL2PScontext, 'this', _gl2ps.new_GL2PScontext(*args))
        _swig_setattr(self, GL2PScontext, 'thisown', 1)
    def __del__(self, destroy=_gl2ps.delete_GL2PScontext):
        try:
            if self.thisown: destroy(self)
        except: pass

class GL2PScontextPtr(GL2PScontext):
    def __init__(self, this):
        _swig_setattr(self, GL2PScontext, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, GL2PScontext, 'thisown', 0)
        _swig_setattr(self, GL2PScontext,self.__class__,GL2PScontext)
_gl2ps.GL2PScontext_swigregister(GL2PScontextPtr)


gl2psPrintPrimitives = _gl2ps.gl2psPrintPrimitives

gl2psBeginPage = _gl2ps.gl2psBeginPage

gl2psEndPage = _gl2ps.gl2psEndPage

gl2psBeginViewport = _gl2ps.gl2psBeginViewport

gl2psEndViewport = _gl2ps.gl2psEndViewport

gl2psText = _gl2ps.gl2psText

gl2psDrawPixels = _gl2ps.gl2psDrawPixels

gl2psEnable = _gl2ps.gl2psEnable

gl2psDisable = _gl2ps.gl2psDisable

gl2psPointSize = _gl2ps.gl2psPointSize

gl2psLineWidth = _gl2ps.gl2psLineWidth

gl2psTextOpt = _gl2ps.gl2psTextOpt

