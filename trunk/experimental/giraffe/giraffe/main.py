import sys
from OpenGL.GL import *
from OpenGL.GLU import *

from giraffe.gui import Window, Button, Box, Application, Shell, List, \
                        Splitter, Label, Tree, TreeNode, Notebook, MainPanel, \
                        OpenGLWidget, Table, Action, Menu, Menubar, Toolbar

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
        Window.__init__(self, statusbar=True)

        # for example
        self.main = MainPanel(self)

        self.shell = ScriptWindow(self.main.bottom_panel,
                                  page_label='console', page_pixmap='console.png')
        self.explorer = ProjectExplorer(self.main.left_panel,
                                        page_label='explorer', page_pixmap='stock_navigator.png')

        book = Notebook(self.main)
        box = Box(book, 'vertical', page_label='window1')
        Label(box, 'periex')
        koalaki = MainPanel(book, page_label='window2')
        Label(koalaki, 'perierxx')
        self.expl = Table(koalaki.right_panel, TableData(),
                          page_label='koalaki', page_pixmap='stock_navigator.png')

        self.test = OpenGLWidget(koalaki.right_panel,
                                 page_label='koali', page_pixmap='graph.png')
        self.test.connect('initialize-gl', self.ini)
        self.test.connect('paint-gl', self.ini)
        self.test.connect('resize-gl', self.res)

        menubar = Menubar(self)
        actions = {
            'file-new': Action('New', 'Create a new project', self.koal),
            'file-open': Action('Open', 'Open a project', self.koal),
            'file-save': Action('Save', 'Save the project', self.koal),
            'edit-undo': Action('Undo', 'Undo the last action', self.koal, 'stock_undo.png'),
            'edit-redo': Action('Redo', 'Redo the last action', self.koal),
            'edit-copy': Action('Copy', 'Undo the last action', self.koal),
            None: None,
        }

        menu = Menu(menubar, '&File')
        for item in ['file-new', 'file-open', None, 'file-save']:
            menu.append(actions[item])

        menu = Menu(menubar, '&Edit')
        for item in ['edit-undo', 'edit-redo', None, 'edit-copy']:
            menu.append(actions[item])

        self.toolbar = Toolbar(self)
        self.toolbar.append(actions['edit-undo'])

    def act(self, x, y):
        print 'patataki'

    def ini(self, x=None, y=None):
        glClearColor(0.4, 0.3, 0.7, 1)
        glClear(GL_COLOR_BUFFER_BIT)

    def res(self, width, height):
        glViewport(0, 0, int(width), int(height))

if __name__ == '__main__':
    app = Application(MainWindow)
    app.run()
