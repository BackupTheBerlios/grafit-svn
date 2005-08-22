
class TextPainter(object):
    def __init__(self, graph):
        self.plot = graph

    #########################################################################
    # Rendering text                                                        #
    #########################################################################

    # Text objects are split into chunks, which are fragments
    # that have the same size and the same type (normal, tex, ...)

    # The render_text_chunk_xxx functions return the size of the
    # text fragment and a renderer. The renderer must be called
    # with the position (lower left corner) of the fragment, 
    # to render the text

    def render_text_chunk_symbol(self, text, size, orientation='h'):
        def renderer(x, y):
            try:
                d = self.plot.datasets[int(text)]
            except (ValueError, IndexError):
                print >>sys.stderr, 'error!'
                return 0, 0, 0, None
            xmin, ymin = self.plot.proj(self.plot.xmin, self.plot.ymin)
            xmax, ymax = self.plot.proj(self.plot.xmax, self.plot.ymax)
            glColor4f(d.style.color[0]/256., d.style.color[1]/256., 
                      d.style.color[2]/256., 1.)
            render_symbols(array([x]), array([y]),
                           d.style.symbol, d.style.symbol_size, 
                           xmin, xmax, ymin, ymax)

        return 15, 15, 0, renderer

    def render_text_chunk_normal(self, text, size, orientation='h'):
        fonte = PIL.ImageFont.FreeTypeFont(FONTFILE, size) 
        w, h = fonte.getsize(text)
        _, origin = fonte.getmetrics()
        if orientation == 'v': 
            ww, hh, angle = h, w, 90.0
        else: 
            ww, hh, angle = w, h, 0.0

        def renderer(x, y):
            if self.plot.ps:
                glRasterPos2d(x, y)
                font = FT2Font(str(FONTFILE))
                fontname = font.postscript_name
                gl2ps_TextOpt(text, fontname, size, GL2PS__TEXT_BL, angle)
            else:
                image = PIL.Image.new('L', (w, h), 255)
                PIL.ImageDraw.Draw(image).text((0, 0), text, font=fonte)
                image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
                if orientation == 'v':
                    image = image.transpose(PIL.Image.ROTATE_270)
                glRasterPos2d(x, y)
#                ww, wh = image.size
                glDrawPixels(ww, hh, GL_LUMINANCE, GL_UNSIGNED_BYTE, image.tostring())

        return ww, hh, origin, renderer

    def render_text_chunk_tex(self, text, size, orientation='h'):
        """Render a text chunk using mathtext"""
        if self.plot.ps:
            w, h, _, pswriter = mathtext.math_parse_s_ps(text, 72, size)
            _, _, origin, _ = mathtext.math_parse_s_ft2font(text, 72, size) #FIXME
        else:
            w, h, origin, fonts = mathtext.math_parse_s_ft2font(text, 72, size)
#        print >>sys.stderr, w, h, origin, text, self.plot.res, self.plot.ps
        if orientation == 'v': 
            ww, hh, angle = h, w, 90
        else: 
            ww, hh, angle = w, h, 0
        def renderer(x, y):
            if self.plot.ps:
                text = pswriter.getvalue()
                ps = "gsave\n%f %f translate\n%f rotate\n%s\ngrestore\n" \
                    % ((self.plot.marginl+x)*self.plot.res, 
                       (self.plot.marginb+y)*self.plot.res, angle, text)
                self.plot.pstext.append(ps)
            else:
                glRasterPos2d(x, y)
                w, h, imgstr = fonts[0].image_as_str()
                N = w*h
                Xall = zeros((N,len(fonts)), typecode=UInt8)

                for i, f in enumerate(fonts):
                    if orientation == 'v':
                        f.horiz_image_to_vert_image()
                    w, h, imgstr = f.image_as_str()
                    Xall[:,i] = fromstring(imgstr, UInt8)

                Xs = mlab.max(Xall, 1)
                Xs.shape = (h, w)

                pa = zeros(shape=(h,w,4), typecode=UInt8)
                rgb = (0., 0., 0.)
                pa[:,:,0] = int(rgb[0]*255)
                pa[:,:,1] = int(rgb[1]*255)
                pa[:,:,2] = int(rgb[2]*255)
                pa[:,:,3] = Xs[::-1]

                glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, pa.tostring())

        return ww, hh, origin, renderer

    def render_text(self, text, size, x, y, align_x='center', align_y='center', 
                    orientation='h', measure_only=False):
        if not '\n' in text:
            return self.render_text_line(text, size, x, y, align_x, align_y, orientation, measure_only)

        lines = text.splitlines()

        heights = []
        widths = []

        for line in lines:
            w, h = self.render_text_line(line, size, x, y, align_x, align_y, orientation, measure_only=True)
            heights.append(h)
            widths.append(w)

        if orientation == 'h':
            totalh = sum(heights)
            totalw = max(widths)
        elif orientation=='v':
            totalh = max(heights)
            totalw = sum(widths)

        for line, off in zip(lines, [0]+list(cumsum(heights))[:-1]):
            self.render_text_line(line, size, x, y-off, align_x, align_y, orientation)

    def render_text_line(self, text, size, x, y, align_x='center', align_y='center', 
                    orientation='h', measure_only=False):
        if text == '':
            return 0, 0

        # split text into chunks
        chunks = cut(text, '$')

        renderers = []
        widths = []
        heights = []
        origins = []
        for chunk, tex in chunks:
            if tex:
                w, h, origin, renderer = self.render_text_chunk_tex('$'+chunk+'$', int(size*1.3), orientation)
                if w!=0 and h!=0:
                    renderers.append(renderer)
                    widths.append(w)
                    heights.append(h)
                    origins.append(origin)
            else:
                chunks2 = cut(chunk, '@')
                for chunk2, at in chunks2:
                    if at:
                        w, h, origin, renderer = self.render_text_chunk_symbol(chunk2, size, orientation)
                    else:
                        w, h, origin, renderer = self.render_text_chunk_normal(chunk2, size, orientation)
                    if w!=0 and h!=0:
                        renderers.append(renderer)
                        widths.append(w)
                        heights.append(h)
                        origins.append(origin)

        #####################################################################
        #                                    ________        _____          #
        #             ___                   | |      |      |     |         #
        #     ___    |   |    ^           __|_|___ _o|      |     |         #
        #    |   |___|   |    |          |    |   |         |_____|         #
        #    |___|___|___|  totalh     __|____|__o|         |     |   ^     #
        #    |o__|   |o__|    |       |       |  |          |     | origin  #
        #        |o__|        v       |_______|_o|          |o____|   v     #
        #                                                                   #
        #####################################################################

        # compute offsets for each chunk and total size 
        if orientation == 'h':
            hb = max(origins)
            ht = max(h-o for h, o in zip(heights, origins))
            totalw, totalh = sum(widths), hb+ht
            offsets = [hb-o for o in origins]
        elif orientation == 'v':
            hb = max(origins)
            ht = max(h-o for h, o in zip(widths, origins))
            totalw, totalh = hb+ht, sum(heights)
            if self.plot.ps:
                offsets = [ht-v-totalw for v in (h-o for h, o in zip(widths, origins))]
            else:
                offsets = [v-ht for v in (h-o for h, o in zip(widths, origins))]

        if measure_only:
            # return width and height of text, in mm
            return totalw/self.plot.res, totalh/self.plot.res

        # alignment (no change = bottom left)
        if align_x == 'right': 
            x -= totalw/self.plot.res
        elif align_x == 'center': 
            x -= (totalw/2)/self.plot.res

        if align_y == 'top': 
            y -= totalh/self.plot.res
        elif align_y == 'center': 
            y -= (totalh/2)/self.plot.res

        # render chunks
        if orientation == 'h':
            for rend, pos, off in zip(renderers, [0]+list(cumsum(widths)/self.plot.res)[:-1], offsets):
                rend(x+pos, y+off/self.plot.res)
        elif orientation == 'v':
            for rend, pos, off in zip(renderers, [0]+list(cumsum(heights)/self.plot.res)[:-1], offsets):
                rend(x-off/self.plot.res, y+pos)



import os
import binascii
from matplotlib.mathtext import math_parse_s_ps, bakoma_fonts
from matplotlib.ft2font import FT2Font

def encodeTTFasPS(fontfile):
    """
    Encode a TrueType font file for embedding in a PS file.
    """
    font = file(fontfile, 'rb')
    hexdata, data = [], font.read(65520)
    b2a_hex = binascii.b2a_hex
    while data:
        hexdata.append('<%s>\n' %
                       '\n'.join([b2a_hex(data[j:j+36]).upper()
                                  for j in range(0, len(data), 36)]) )
        data  = font.read(65520)

    hexdata = ''.join(hexdata)[:-2] + '00>'
    font    = FT2Font(str(fontfile))

    headtab  = font.get_sfnt_table('head')
    version  = '%d.%d' % headtab['version']
    revision = '%d.%d' % headtab['fontRevision']

    dictsize = 8
    fontname = font.postscript_name
    encoding = 'StandardEncoding'
    fontbbox = '[%d %d %d %d]' % font.bbox

    posttab  = font.get_sfnt_table('post')
    minmemory= posttab['minMemType42']
    maxmemory= posttab['maxMemType42']

    infosize = 7
    sfnt     = font.get_sfnt()
    notice   = sfnt[(1,0,0,0)]
    family   = sfnt[(1,0,0,1)]
    fullname = sfnt[(1,0,0,4)]
    iversion = sfnt[(1,0,0,5)]
    fixpitch = str(bool(posttab['isFixedPitch'])).lower()
    ulinepos = posttab['underlinePosition']
    ulinethk = posttab['underlineThickness']
    italicang= '(%d.%d)' % posttab['italicAngle']

    numglyphs = font.num_glyphs
    glyphs = []
    for j in range(numglyphs):
        glyphs.append('/%s %d def' % (font.get_glyph_name(j), j))
        if j != 0 and j%4 == 0:
            glyphs.append('\n')
        else:
            glyphs.append(' ')
    glyphs = ''.join(glyphs)
    data = ['%%!PS-TrueType-%(version)s-%(revision)s\n' % locals()]
    if maxmemory:
        data.append('%%%%VMusage: %(minmemory)d %(maxmemory)d' % locals())
    data.append("""%(dictsize)d dict begin
/FontName /%(fontname)s def
/FontMatrix [1 0 0 1 0 0] def
/FontType 42 def
/Encoding %(encoding)s def
/FontBBox %(fontbbox)s def
/PaintType 0 def
/FontInfo %(infosize)d dict dup begin
/Notice (%(notice)s) def
/FamilyName (%(family)s) def
/FullName (%(fullname)s) def
/version (%(iversion)s) def
/isFixedPitch %(fixpitch)s def
/UnderlinePosition %(ulinepos)s def
/UnderlineThickness %(ulinethk)s def
end readonly def
/sfnts [
%(hexdata)s
] def
/CharStrings %(numglyphs)d dict dup begin
%(glyphs)s
end readonly def
FontName currentdict end definefont pop""" % locals())
    return ''.join(data)

