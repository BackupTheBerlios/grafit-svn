import sys

from giraffe.gui import Window, Button, Box, Application, Shell, List, Splitter, Label, Tree, TreeNode, Notebook, MainPanel

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
        Window.__init__(self, menubar=True, statusbar=True, toolbar=True)

        # for example
        self.main = MainPanel(self)

        self.shell = ScriptWindow(self.main.bottom_panel,
                                  page_label='console', page_pixmap='console.png')
        self.explorer = ProjectExplorer(self.main.left_panel,
                                        page_label='explorer', page_pixmap='stock_navigator.png')

        book = Notebook(self.main)
        box = Box(book, 'vertical', page_label='koali.fasmata.data.perthcops.maniquio')
        Label(box, 'periex')
        for i in xrange(10):
            koalaki = MainPanel(book, page_label='arrhenius.nr2_5min_2percent.koalaki')
        Label(koalaki, 'perierxx')
        self.test = ProjectExplorer(koalaki.right_panel,
                                    page_label='poulorer', page_pixmap='stock_navigator.png')
        self.test = ProjectExplorer(koalaki.right_panel,
                                    page_label='poulouir', page_pixmap='graph.png')



if __name__ == '__main__':
    app = Application(MainWindow)
    app.run()
