import sys

from giraffe.gui import Window, Button, Box, Application, Shell

class ScriptWindow(Shell):
    def __init__(self, parent, **kwds):
        self.locals = {}
        Shell.__init__(self, parent, locals=self.locals, **kwds)

        self.run('from giraffe.worksheet.arrays import *')
        self.run('from giraffe.worksheet.arrays import *')
        self.run('from giraffe import *')

        self.clear()
        self.prompt()

    def connect_project(self, project):
        self.project = project
        self.locals.update({'project': project})
        self.push('project.set_dict(globals())')

    def disconnect_project(self):
        self.locals.update({'project': None})
        self.project.unset_dict()
        self.project = None


# example main window
class MainWindow(Window):
    def __init__(self):
        Window.__init__(self, menubar=True, statusbar=True, panels='br')

        # for example
        self.shell = ScriptWindow(self.bottom_panel,
                                  page_label='console', page_pixmap='console.png')

        box = Box(self, 'vertical')
        self.m = Button(box, 'periex')
        self.m2 = Button(box, 'px')


if __name__ == '__main__':
    app = Application(MainWindow)
    app.run()
