#!/usr/bin/env python

# This program displays a simple window and has a simple callback for
# when the OK button is clicked.

import gtk
import gtk.glade

# libglade needs some way to lookup the handler functions; defining
# them in a class provides an easy way to do that
class GladeHandlers:

  def ok_button_clicked(ok_button):
    print "Thanks for trying out my program."
    gtk.mainquit()

  # No predefined helper functions exist--all must be manually declared.
  def gtk_main_quit(window, event):
    gtk.mainquit()

# load the interface
main_window = gtk.glade.XML('project1.glade')

# connect the signals in the interface
main_window.signal_autoconnect(GladeHandlers.__dict__)

# start the event loop
gtk.main()
