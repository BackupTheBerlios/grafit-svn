import gtk
import gtk.glade

#import pygtk
#pygtk.require('2.0')
#import gtk
import pango

#win = gtk.Window()
#win.show()
#vbox = gtk.VBox()
#vbox.show()
#win.add(vbox)

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

def rotated_image(image):
    imageOut = gtk.gdk.Image(type=0,
#                             visual=pixmap.get_visual(),
                             width=h, height=w)
    imageOut.set_colormap(imageIn.get_colormap())
    for i in range(w):
        for j in range(h):
            imageOut.put_pixel(j, i, imageIn.get_pixel(w-i-1,j) )
    return imageOut


class GladeHandlers:

    def ok_button_clicked(ok_button):
        print "Thanks for trying out my program."
        gtk.mainquit()

    def gtk_main_quit(window, event):
        gtk.mainquit()

    def on_script_toggled(*args, **kwds):
        if main_window.get_widget('script_button').get_active():
            main_window.get_widget('script').show()
        else:
            main_window.get_widget('script').hide()
        print args, kwds

# load the interface
main_window = gtk.glade.XML('project1.glade')

print main_window.get_widget('image9')

# connect the signals in the interface
main_window.signal_autoconnect(GladeHandlers.__dict__)

# start the event loop
gtk.main()
