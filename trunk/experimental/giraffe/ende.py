import pygtk
pygtk.require('2.0')
import gtk
import pango

win = gtk.Window()
win.show()
vbox = gtk.VBox()
vbox.show()
win.add(vbox)

class C:

    def __init__(self, text):
        self.text = text

    def realize(self, drawingArea):
        self.drawingArea = drawingArea
        self.drawable = drawingArea.window

        # text properties
        context = self.drawingArea.create_pango_context()
        self.layout  = self.drawingArea.create_pango_layout(self.text)
        desc = pango.FontDescription('Sans 14')
        self.layout.set_font_description(desc)


    def draw_text(self, drawable=None, x=100, y=100):
        if drawable is None: drawable=self.drawable

        # draw some text in the foreground color
        gc = drawable.new_gc()
        drawable.draw_layout(gc, x=x, y=y, layout=self.layout)



    def draw_text_rotated(self):
        """
        draw the text to a pixmap, rotate the image, fill a pixbuf
        and draw from the pixbuf
        """

        inkRect, logicalRect = self.layout.get_pixel_extents()
        x, y, w, h = logicalRect
        winw, winh = self.drawable.get_size()

        self.drawable.clear_area(50, 100, h, w)
        imageIn = self.drawable.get_image(x=50, y=100, width=h, height=w)
        imageOut = gtk.gdk.Image(type=0,
                                 visual=self.drawable.get_visual(),
                                 width=w, height=h)
        imageOut.set_colormap(imageIn.get_colormap())
        for i in range(h):
            for j in range(w):
                imageOut.put_pixel(j, i, imageIn.get_pixel(i,w-j-1) )

        pixmap = gtk.gdk.Pixmap(self.drawable, winw, winh)
        gc = pixmap.new_gc()
        pixmap.draw_image(gc, imageOut, 0, 0, 0, 0, w, h)
        c.draw_text(drawable=pixmap, x=0, y=0)

        if 0:
            # These lines test that the pixmap was drawn to ok
            pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, w, h)
            pixbuf.get_from_drawable(pixmap, pixmap.get_colormap(),
                                     0, 0, 0, 0, w, h)
            pixbuf.render_to_drawable(self.drawable, gc, 0, 0, 0, 0, w, h, 0, 0, 0)
            return


        imageIn = pixmap.get_image(x=0, y=0, width=w, height=h)
        imageOut = gtk.gdk.Image(type=0,
                                 visual=pixmap.get_visual(),
                                 width=h, height=w)
        imageOut.set_colormap(imageIn.get_colormap())
        for i in range(w):
            for j in range(h):
                imageOut.put_pixel(j, i, imageIn.get_pixel(w-i-1,j) )


        self.drawable.draw_image(gc, imageOut, 0, 0, 50, 100, h, w)


c = C('Some text')

da = gtk.DrawingArea()
da.connect('realize', c.realize)
da.set_size_request(300,300)


da.show()
vbox.pack_start(da, gtk.TRUE, gtk.TRUE)

hbox = gtk.HBox()
hbox.show()
vbox.pack_start(hbox, gtk.FALSE, gtk.FALSE)

button = gtk.Button('Draw')
button.show()
button.connect('clicked', lambda b: c.draw_text())
hbox.pack_start(button, gtk.TRUE, gtk.TRUE)

button = gtk.Button('Rotate')
button.show()
button.connect('clicked', lambda b: c.draw_text_rotated())
hbox.pack_start(button, gtk.TRUE, gtk.TRUE)

button = gtk.Button('Quit')
button.show()
button.connect('clicked', lambda b: gtk.mainquit())
hbox.pack_start(button, gtk.TRUE, gtk.TRUE)

gtk.mainloop()



