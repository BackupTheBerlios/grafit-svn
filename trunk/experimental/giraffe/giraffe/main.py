import sys
from OpenGL.GL import *
from OpenGL.GLU import *

from giraffe.gui import Window, Button, Box, Application, Shell, List, \
                        Splitter, Label, Tree, TreeNode, Notebook, MainPanel, \
                        OpenGLWidget, Table

from giraffe.signals import HasSignals

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

class ProjectExplorer(Box):
    def __init__(self, parent, **kwds):
        Box.__init__(self, parent, 'horizontal', **kwds)
        self.splitter = Splitter(self, 'horizontal')
        self.tree = Tree(self.splitter)
        n = TreeNode()
        n.append(TreeNode())
        n.append(TreeNode())
        n.append(TreeNode())
        self.tree.append(n)
        self.list2 = List(self.splitter)

class TableData(HasSignals):
    def get_n_columns(self):
        return 200

    def get_n_rows(self):
        return 20000

    def get_column_name(self, col):
        return 'c'

    def get_row_name(self, row):
        return 'r'

    def get_data(self, col, row):
        return str(col + row)


# example main window
class MainWindow(Window):
    def __init__(self):
        Window.__init__(self, menubar=True, statusbar=True, toolbar=True)

        # for example
        self.main = MainPanel(self)

        self.shell = ScriptWindow(self.main.bottom_panel,
                                  page_label='console', page_pixmap='console.png')
        self.explorer = ProjectExplorer(self.main.left_panel,
                                        page_label='explorer', page_pixmap='stock_navigator.png')

        book = Notebook(self.main)
        box = Box(book, 'vertical', page_label='koali.fasmata.maniquio')
        Label(box, 'periex')
        koalaki = MainPanel(book, page_label='arrhenius.koalaki')
        Label(koalaki, 'perierxx')
        self.expl = Table(koalaki.right_panel, TableData(),
                          page_label='poulorer', page_pixmap='stock_navigator.png')

        self.test = OpenGLWidget(koalaki.right_panel,
                                 page_label='poulouir', page_pixmap='graph.png')
        self.test.connect('initialize-gl', self.ini)
        self.test.connect('paint-gl', self.ini)
        self.test.connect('resize-gl', self.res)

    def ini(self, x=None, y=None):
        print 'a', x, y
        glClearColor(0.4, 0.3, 0.7, 1)
        glClear(GL_COLOR_BUFFER_BIT)

    def res(self, width, height):
        glViewport(0, 0, int(width), int(height))

if __name__ == '__main__':
    app = Application(MainWindow)
    app.run()
