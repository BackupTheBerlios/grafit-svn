import sys

from giraffe.gui import Window, Button, Box, Application, Shell, List, Splitter, Label, Tree, TreeNode, Notebook

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


# example main window
class MainWindow(Window):
    def __init__(self):
        sys.stderr.write('main')
        Window.__init__(self, menubar=True, statusbar=True, toolbar=True, panels='brl')

        # for example
        sys.stderr.write('script')
        self.shell = ScriptWindow(self.bottom_panel,
                                  page_label='console', page_pixmap='console.png')
        sys.stderr.write('explorer')
        self.explorer = ProjectExplorer(self.left_panel,
                                        page_label='explorer', page_pixmap='stock_navigator.png')
        sys.stderr.write('ok')

        book = Notebook(self)
        box = Box(book, 'vertical', page_label='koali')
        Label(box, 'periex')
        box = Box(book, 'vertical', page_label='petaloudi')
        Label(box, 'perierxx')


if __name__ == '__main__':
    sys.stderr.write('ok\n')
    app = Application(MainWindow)
    app.run()
