import sys
from OpenGL.GL import *
from OpenGL.GLU import *

from giraffe.gui import Window, Button, Box, Application, Shell, List, \
                        Splitter, Label, Tree, TreeNode, Notebook, MainPanel, \
                        OpenGLWidget, Table, Action, Menu, Menubar, Toolbar

import wx
import os

from giraffe.signals import HasSignals

from giraffe import *

class Cancel(Exception):
    pass

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
        self.run('project.set_dict(globals())')

    def disconnect_project(self):
        self.locals.update({'project': None})
        self.project.unset_dict()
        self.project = None


class FolderTreeNode(HasSignals):
    """Adapter from a folder to a Tree node"""

    def __init__(self, folder, isroot=False):
        self.folder = folder
        if isroot:
            self.folder.project.connect('add-item', self.on_modified)
            self.folder.project.connect('remove-item', self.on_modified)

    def __iter__(self):
        for item in self.folder.contents():
            if isinstance(item, Folder):
                yield FolderTreeNode(item)
    
    def __str__(self): 
        return self.folder.name

    def get_pixmap(self): 
        return 'stock_folder.png'

    def on_modified(self, item): 
        self.emit('modified')


class ProjectExplorer(Box):
    def __init__(self, parent, **kwds):
        Box.__init__(self, parent, 'horizontal', **kwds)
        self.splitter = Splitter(self, 'horizontal')
        self.tree = Tree(self.splitter)
        self.list = List(self.splitter)
        self.tree.connect('selected', self.on_tree_selected)

    def on_tree_selected(self, item):
        self.list.model = FolderListData(item.folder)
        self.project.cd(item.folder)

    def connect_project(self, project):
        self.project = project
        self.tree.append(FolderTreeNode(self.project.top, isroot=True))

    def disconnect_project(self):
        self.project = None
        self.tree.clear()

class FolderListData(HasSignals):
    def __init__(self, folder):
        self.folder = folder

    def __len__(self): 
        return len(list(self.folder.contents()))

    def get(self, row, column): 
        return list(self.folder.contents())[row].name

    def get_image(self, row): 
        return { Worksheet: 'worksheet.png',
                 Graph: 'graph.png',
                 Folder: 'stock_folder.png', }[type(list(self.folder.contents())[row])]

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
            'file-new': Action('New', 'Create a new project', self.on_project_new),
            'file-open': Action('Open', 'Open a project', self.on_project_open),
            'file-save': Action('Save', 'Save the project', self.on_project_save),
            'edit-undo': Action('Undo', 'Undo the last action', self.koal, 'stock_undo.png'),
            'edit-redo': Action('Redo', 'Redo the last action', self.koal),
            'edit-copy': Action('Copy', 'Undo the last action', self.koal),
            'object-new-worksheet': Action('New Worksheet', 'Create a new worksheet', 
                                           self.on_new_worksheet, 'worksheet.png'),
            'object-new-graph': Action('New Graph', 'Create a new worksheet', 
                                       self.on_new_graph, 'graph.png'),
            'object-new-folder': Action('New Folder', 'Create a new worksheet', 
                                        self.on_new_folder, 'stock_folder.png'),
            None: None
        }

        menu = Menu(menubar, '&File')
        for item in ['file-new', 'file-open', None, 'file-save']:
            menu.append(actions[item])

        menu = Menu(menubar, '&Edit')
        for item in ['edit-undo', 'edit-redo', None, 'edit-copy']:
            menu.append(actions[item])

        self.toolbar = Toolbar(self)
        for item in ['object-new-folder', 'object-new-worksheet', 'object-new-graph']:
            self.toolbar.append(actions[item])

        self.project = Project()
        self.project.new(Folder, 'arse')
        self.project.new(Worksheet, 'brse')
        self.project.new(Graph, 'crse')
        self.project.new(Folder, 'drse')

        self.open_project(self.project)
        f = self.project.new(Folder, 'erse')
        self.project.new(Folder, 'frse', f)
        self.project.new(Folder, 'grse', f)

    def open_project(self, project):
        self.project = project
        for panel in (self.shell, self.explorer):
            panel.connect_project(self.project)
#        self.project.connect('remove-item', self.on_project_remove_item)
#        command_list.clear()

    def close_project(self):
        for panel in (self.shell, self.explorer):
            panel.disconnect_project()
#        self.project.disconnect('remove-item', self.on_project_remove_item)

    def act(self, x, y):
        print 'patataki'

    def ini(self, x=None, y=None):
        glClearColor(0.4, 0.3, 0.7, 1)
        glClear(GL_COLOR_BUFFER_BIT)

    def res(self, width, height):
        glViewport(0, 0, int(width), int(height))

    def on_new_worksheet(self):
        ws = self.project.new(Worksheet, None, self.project.here)
        ws.a = [1,2,3]
        ws.other = 2*ws.a

    def on_project_open(self):
        try:
            if self.project.modified and self.ask_savechanges():
                self.on_project_save()

            dlg = wx.FileDialog(self._widget, message="Choose a file", defaultDir=os.getcwd(), 
                                defaultFile="", wildcard="All Files|*.*|Projects|*.mk", style=wx.OPEN | wx.CHANGE_DIR)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPaths()[0]
                self.close_project()
                self.open_project(Project(str(path)))
            dlg.Destroy()
        except Cancel:
            return

    def ask_savechanges(self):
        dlg = wx.MessageDialog(self._widget, 'Save <b>changes?</b>', 'Save?',
                               wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            return True
        elif result == wx.ID_NO:
            return False
        elif result == wx.ID_CANCEL:
            raise Cancel
        dlg.Destroy()

    def on_project_saveas(self):
        try:
            dlg = wx.FileDialog(self._widget, message="Choose a file", defaultDir=os.getcwd(), 
                                defaultFile="", wildcard="All Files|*.*|Projects|*.mk", style=wx.SAVE | wx.CHANGE_DIR)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPaths()[0]
                self.project.saveto(path)
                self.open_project(Project(str(path)))
            dlg.Destroy()
        except Cancel:
            return

    def on_project_save(self):
        try:
            if self.project.filename is not None:
                self.project.commit()
            else:
                self.on_project_saveas()
        except Cancel:
            return

    def on_project_new(self):
        try:
            if self.project.modified and self.ask_savechanges():
                self.on_project_save()
            self.close_project()
            self.open_project(Project())
        except Cancel:
            return
            
    def on_new_graph(self):
        g = self.project.new(Graph, None, self.project.here)

    def on_new_folder(self):
        self.project.new(Folder, None, self.project.here)


if __name__ == '__main__':
    app = Application(MainWindow)
    app.run()
