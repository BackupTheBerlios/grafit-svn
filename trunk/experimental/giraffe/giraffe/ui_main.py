import sys

from giraffe.gui import Window, Button, Box, Application, Shell, List, \
                        Splitter, Label, Tree, TreeNode, Notebook, MainPanel, \
                        OpenGLWidget, Table, Action, Menu, Menubar, Toolbar

from giraffe.ui_worksheet_view import WorksheetView
from giraffe.ui_graph_view import GraphView

import wx
import os

from giraffe.signals import HasSignals
from giraffe.commands import command_list

from giraffe import *

class Cancel(Exception):
    pass

class ScriptWindow(Shell):
    def __init__(self, parent, **kwds):
        self.locals = {}
        Shell.__init__(self, parent, locals=self.locals, **kwds)

        self.run('from giraffe.arrays import *')
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
        self.list.connect('item-activated', self.on_list_item_activated)

    def on_tree_selected(self, item):
        self.list.model = FolderListData(item.folder)
        self.project.cd(item.folder)

    def on_list_item_activated(self, item):
        self.emit('item-activated', self.list.model[item])

    def connect_project(self, project):
        self.project = project
        root = FolderTreeNode(self.project.top, isroot=True)
        self.tree.append(root)
        self.on_tree_selected(root)

    def disconnect_project(self):
        self.project = None
        self.tree.clear()

class ActionListModel(HasSignals):
    def __init__(self, actionlist):
        self.actionlist = actionlist
        self.actionlist.connect('added', self.on_modified)
        self.actionlist.connect('removed', self.on_modified)

    def on_modified(self, command):
        self.emit('modified')
        
    # list model interface
    def get(self, row, column): return str(self.actionlist.commands[row])
    def get_image(self, row): return None
    def __len__(self): return len(self.actionlist.commands)

class ActionList(List):
    def __init__(self, actionlist, parent, **place):
        List.__init__(self, parent, model=ActionListModel(actionlist), **place)

class FolderListData(HasSignals):
    def __init__(self, folder):
        self.folder = folder
        self.folder.project.connect('add-item', self.on_project_modified)
        self.folder.project.connect('remove-item', self.on_project_modified)

    def on_project_modified(self, item):
        if item.parent == self.folder:
            self.emit('modified')

    def __len__(self): 
        return len(list(self.folder.contents()))

    def __getitem__(self, key):
        return list(self.folder.contents())[key]

    def get(self, row, column): 
        return list(self.folder.contents())[row].name

    def get_image(self, row): 
        return { Worksheet: 'worksheet.png',
                 Graph: 'graph.png',
                 Folder: 'stock_folder.png', }[type(list(self.folder.contents())[row])]

# example main window
class MainWindow(Window):
    def __init__(self):
        Window.__init__(self, statusbar=True)

        # for example
        self.main = MainPanel(self)

        self.shell = ScriptWindow(self.main.bottom_panel,
                                  page_label='console', page_pixmap='console.png')
        self.shell.locals['mainwin'] = self
        self.explorer = ProjectExplorer(self.main.left_panel,
                                        page_label='explorer', page_pixmap='stock_navigator.png')
        self.actionlist = ActionList(command_list, self.main.left_panel,
                                        page_label='actions', page_pixmap='stock_undo.png')
        self.explorer.connect('item-activated', self.on_item_activated)

        self.project = Project()
        self.open_project(self.project)

        self.book = Notebook(self.main)
        self.book.connect('page-changed', self.on_page_changed)

        menubar = Menubar(self)
        actions = {
            'file-new': Action('New', 'Create a new project', self.on_project_new, 'new.png'),
            'file-open': Action('Open', 'Open a project', self.on_project_open, 'open.png'),
            'file-save': Action('Save', 'Save the project', self.on_project_save, 'save.png'),
            'file-saveas': Action('Save As', 'Save the project with a new name', self.on_project_saveas, 'saveas.png'),
            'edit-undo': Action('Undo', 'Undo the last action', object, 'stock_undo.png'),
            'edit-redo': Action('Redo', 'Redo the last action', object),
            'edit-copy': Action('Copy', 'Undo the last action', object),
            'object-new-worksheet': Action('New Worksheet', 'Create a new worksheet', 
                                           self.on_new_worksheet, 'worksheet.png'),
            'object-new-graph': Action('New Graph', 'Create a new worksheet', 
                                       self.on_new_graph, 'graph.png'),
            'object-new-folder': Action('New Folder', 'Create a new worksheet', 
                                        self.on_new_folder, 'stock_folder.png'),
            None: None
        }

        menu = Menu(menubar, '&File')
        for item in ['file-new', 'file-open', None, 'file-save', 'file-saveas']:
            menu.append(actions[item])

        menu = Menu(menubar, '&Edit')
        for item in ['edit-undo', 'edit-redo', None, 'edit-copy']:
            menu.append(actions[item])

        self.toolbar = Toolbar(self)
        for item in ['file-new', 'file-open', 'file-save', 'file-saveas', None,
                     'object-new-folder', 'object-new-worksheet', 'object-new-graph']:
            self.toolbar.append(actions[item])

    def open_project(self, project):
        self.project = project
        for panel in (self.shell, self.explorer):
            panel.connect_project(self.project)
#        self.project.connect('remove-item', self.on_project_remove_item)
#        command_list.clear()

    def on_item_activated(self, item):
        if isinstance(item, Graph):
            for view in [v for v in self.book.pages if hasattr(v, 'graph')]:
                if item == view.graph:
                    self.book.select(view)
                    return
            w = GraphView(self.book, item, page_label=item.name, page_pixmap='graph.png')
            self.book.select(w)
        elif isinstance(item, Worksheet):
            for view in [v for v in self.book.pages if hasattr(v, 'worksheet')]:
                if item == view.worksheet:
                    self.book.select(view)
                    return
            w = WorksheetView(self.book, item, page_label=item.name, page_pixmap='worksheet.png')
            self.book.select(w)

    def on_page_changed(self, item):
#        if isinstance(item, GraphView):
#            item.graph.emit('redraw')
        pass

    def close_project(self):
        for panel in (self.shell, self.explorer):
            panel.disconnect_project()
        for page in list(self.book.pages):
            self.book.delete(page)
#        self.project.disconnect('remove-item', self.on_project_remove_item)

    def act(self, x, y):
        print 'patataki'

    def on_new_worksheet(self):
        ws = self.project.new(Worksheet, None, self.project.here)
        ws.a = [1,2,3]
        ws.other = 2*ws.a

    def on_project_open(self):
        try:
            if self.project.modified and self.ask_savechanges():
                self.on_project_save()

            dlg = wx.FileDialog(self._widget, message="Choose a file", defaultDir=os.getcwd(), 
                                defaultFile="", wildcard="All Files|*.*|Projects|*.gt", style=wx.OPEN | wx.CHANGE_DIR)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPaths()[0]
                self.close_project()
                self.open_project(Project(str(path)))
                command_list.clear()
            dlg.Destroy()
        except Cancel:
            return

    def ask_savechanges(self):
        dlg = wx.MessageDialog(self._widget, 'Save changes to this project?', 'Save?',
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
                command_list.clear()
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
            command_list.clear()
        except Cancel:
            return
            
    def on_new_graph(self):
        g = self.project.new(Graph, None, self.project.here)

    def on_new_folder(self):
        self.project.new(Folder, None, self.project.here)


if __name__ == '__main__':
    app = Application(MainWindow)
    app.run()
