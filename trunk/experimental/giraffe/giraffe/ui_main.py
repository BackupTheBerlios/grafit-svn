import sys
print >>sys.stderr, "import worksheet_view"
from giraffe.ui_worksheet_view import WorksheetView
print >>sys.stderr, "import graph_view"
from giraffe.ui_graph_view import GraphView
from giraffe.import_ascii import import_ascii

import wx
import os
import tempfile

from giraffe.signals import HasSignals, global_connect
from giraffe.commands import command_list, undo, redo

from giraffe import Graph, Worksheet, Folder, Project

from giraffe.gui import Window, Button, Box, Application, Shell, List, \
                        Splitter, Label, Tree, TreeNode, Notebook, MainPanel, \
                        OpenGLWidget, Table, Action, Menu, Menubar, Toolbar

import giraffe.signals

from settings import settings

class ItemDragData(object):
    def __init__(self, items):
        self.items = items
    
    supported_formats = ['grafit-object', 'filename']

    def get_data(self, format):
        if format == 'grafit-object':
            return '\n'.join(i.id for i in self.items)
        elif format == 'filename':
            r = []
            for item in self.items:
                if isinstance(item, Worksheet):
                    filename = item.name + '.txt'
                elif isinstance(item, Graph):
                    filename = item.name + '.ps'
                elif isinstance(item, Folder):
                    filename = item.name
                d = tempfile.mkdtemp()
                f = open(d+'/'+filename, 'wb')
                if isinstance(item, Worksheet) or isinstance(item, Graph):
                    item.export_ascii(f)
                f.close()
                r.append(d+'/'+filename)
            return r

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
    def __new__(cls, folder, **kwds):
        if hasattr(folder, '_treenode'):
            return folder._treenode
        else:
            obj = HasSignals.__new__(cls, folder, **kwds)
            folder._treenode = obj
            return obj

    def __init__(self, folder, isroot=False):
        self.folder = folder
        self.folder.connect('modified', self.on_modified)
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

    def on_modified(self, item=None): 
        self.emit('modified')

    def rename(self, newname):
        if newname == '':
            return False
        else:
            self.folder.name = str(newname)
            self.folder.project.top.emit('modified')
            return True

#    def close(self):
#        print >>sys.stderr, 'close'
#    def open(self):
#        print >>sys.stderr, 'open'

class ProjectExplorer(Box):
    def __init__(self, parent, **kwds):
        Box.__init__(self, parent, 'horizontal', **kwds)
        self.splitter = Splitter(self, 'horizontal')

        self.tree = Tree(self.splitter)
        self.tree.enable_drop(['grafit-object', 'text'])

        self.tree.connect('drop-hover', self.on_drop_hover)
        self.tree.connect('drop-ask', self.on_tree_drop_ask)
        self.tree.connect('dropped', self.on_tree_dropped)

        self.tree.connect('selected', self.on_tree_selected)

        self.list = List(self.splitter)
        self.list.enable_drop(['grafit-object', 'filename', 'text'])
        self.list.connect('drop-hover', self.on_drop_hover)
        self.list.connect('dropped', self.on_dropped)
        self.list.connect('drop-ask', self.on_drop_ask)

        self.list.connect('drag-begin', self.on_begin_drag)
        self.list.connect('item-activated', self.on_list_item_activated)
        self.list.connect('right-click', self.on_list_right_click)

    def on_list_right_click(self, item):
        if item == -1:
            return
        item = self.list.model[item]
        menu = Menu()
        menu.append(Action('Delete', 'delete', object))#, 'open.png'))
        self.list._widget.PopupMenu(menu._menu)


    def on_tree_drop_ask(self, item):
        return True

    def on_tree_dropped(self, item, format, data):
        print >>sys.stderr, "dropped", item, format, item
        if format == 'grafit-object':
            for d in data.split('\n'):
                self.project.items[d].parent = item.folder
        else:
            print 'DROPPED: ', item, format, data

    def on_drop_hover(self, item):
#        if item != -1:
            return 'copy'

    def on_drop_ask(self, item):
        if item != -1 and isinstance(self.list.model[item], Folder):
            return True
        else:
            return True
#            return False

    def on_dropped(self, item, format, data):
        if format == 'grafit-object':
            for d in data.split('\n'):
                self.project.items[d].parent = self.list.model[item]
        elif format == 'filename' and item == -1:
            # import ascii
            for path in data:
                ws = self.project.new(Worksheet, str(os.path.basename(path).split('.')[0]), self.project.here)
                ws.array, ws._header = import_ascii(path)
        else:
            print 'DROPPED: ', format, data

    def on_begin_drag(self, item):
        return ItemDragData([self.list.model[i] for i in self.list.selection])

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
        self.actionlist.connect('modified', self.on_modified)

    def on_modified(self, command=None):
        self.emit('modified')
        
    # list model interface
    def get(self, row, column): 
        com = self.actionlist.commands[row]
        if com.done:
            return str(com)
        else:
            return '('+str(com)+')'
    def get_image(self, row): 
        com = self.actionlist.commands[row]
        if com.done:
            return 'command-done.png'
        else:
            return 'command-undone.png'
    def __len__(self): return len(self.actionlist.commands)

class ActionList(Box):
    def __init__(self, actionlist, parent, **place):
        Box.__init__(self, parent, 'vertical', **place)
        self.list = List(self, model=ActionListModel(actionlist), stretch=1.)
        self.list._widget.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.list.connect('item-activated', self.on_list_item_activated)
        self.list.connect('selection-changed', self.on_list_selection_changed)
        self.label = Label(self, 'Action', stretch=0.)

    def on_list_item_activated(self, idx):
        com = self.list.model.actionlist.commands[idx]
        if com.done:
            while com.done:
                undo()
        else:
            while not com.done:
                redo()

    def on_list_selection_changed(self):
        com = self.list.model.actionlist.commands[self.list.selection[0]]
        self.label.text = str(com)

class FolderListData(HasSignals):
    def __init__(self, folder):
        self.folder = folder
        self.folder.project.connect('add-item', self.on_project_modified)
        self.folder.project.connect('remove-item', self.on_project_modified)
        self.folder.connect('modified', self.on_folder_modified)

    def on_project_modified(self, item):
        if item.parent == self.folder:
            self.emit('modified')

    def on_folder_modified(self):
        self.emit('modified')

    def __len__(self): return len(list(self.folder.contents()))
    def __getitem__(self, key): return list(self.folder.contents())[key]
    def get(self, row, column): return list(self.folder.contents())[row].name
    def get_image(self, row): 
        return { Worksheet: 'worksheet.png',
                 Graph: 'graph.png',
                 Folder: 'stock_folder.png', }[type(list(self.folder.contents())[row])]

# example main window
class MainWindow(Window):
    def __init__(self):
        print >>sys.stderr, "creating main window"
        Window.__init__(self, statusbar=True, size=(800, 600))
        self.title = 'Grafit'

        # for example
        self.main = MainPanel(self)

        self.shell = ScriptWindow(self.main.bottom_panel,
                                  page_label='console', page_pixmap='console.png')
        self.shell.locals['mainwin'] = self

        try:
            self.shell._widget.history = settings.get('script', 'history').split('\n')
        except:
            self.shell._widget.history = []
            pass
        self.explorer = ProjectExplorer(self.main.left_panel,
                                        page_label='project', page_pixmap='stock_navigator.png')
        self.actionlist = ActionList(command_list, self.main.left_panel,
                                        page_label='actions', page_pixmap='stock_undo.png')
        self.explorer.connect('item-activated', self.on_item_activated)

        self.project = Project()
        self.open_project(self.project)

        self.book = Notebook(self.main)
        self.book.connect('page-changed', self.on_page_changed)

        self.main.left_panel.open(self.explorer)

        global_connect('status-message', self.on_status_message)

        actions = {
            'file-new': Action('New', 'Create a new project', self.on_project_new, 'new.png', 'Ctrl+N'),
            'file-open': Action('Open...', 'Open a project', self.on_project_open, 'open.png', 'Ctrl+O'),
            'file-save': Action('Save', 'Save the project', 
                                self.on_project_save, 'save.png', 'Ctrl+S'),
            'file-saveas': Action('Save As...', 'Save the project with a new name', 
                                  self.on_project_saveas, 'saveas.png', 'Ctrl+A'),
            'file-quit': Action('Quit', 'Quit grafit', self.on_quit, 'stock_exit.png', 'Ctrl+Q'),

            'edit-undo': Action('Undo', 'Undo the last action', undo, 'stock_undo.png', 'Ctrl+Z'),
            'edit-redo': Action('Redo', 'Redo the last action', redo, 'stock_redo.png', 'Shift+Ctrl+Z'),
            'edit-copy': Action('Copy', 'Undo the last action', object, None, 'Ctrl+C'),

            'import-ascii': Action('Import ASCII...', 'Import and ASCII file', 
                                   self.on_import_ascii, 'import_ascii.png', 'Ctrl+I'),
            'object-new-worksheet': Action('New Worksheet', 'Create a new worksheet', 
                                           self.on_new_worksheet, 'worksheet.png'),
            'object-new-graph': Action('New Graph', 'Create a new worksheet', 
                                       self.on_new_graph, 'graph.png'),
            'object-new-folder': Action('New Folder', 'Create a new worksheet', 
                                        self.on_new_folder, 'stock_folder.png'),
            None: None
        }

        self.menubar = Menubar(self)
        for title, items in [
            ('&File', ['file-new', 'file-open', None, 
                       'file-save', 'file-saveas', None, 
                       'file-quit']),
            ('&Edit', ['edit-undo', 'edit-redo', None, 
                       'edit-copy']),
            ('&Tools', []),
            ('&Help', []),
        ]:
            menu = Menu(self.menubar, title)
            for item in items:
                menu.append(actions[item])

        self.toolbar = Toolbar(self)
        for item in [
            'file-new', 'file-open', 'file-save', 'file-saveas', None,
            'object-new-folder', 'object-new-worksheet', 'object-new-graph', None,
            'edit-undo', 'edit-redo', None,
            'import-ascii'
        ]:
            self.toolbar.append(actions[item])
        self.toolbar._widget.Realize()

        if len(sys.argv) > 1:
            self.open_project(Project(sys.argv[1]))

        self.connect('close', self.on_quit)

        self.main.bottom_panel._widget.toolbar.Realize()
        self.main.left_panel._widget.toolbar.Realize()
        self.main.right_panel._widget.toolbar.Realize()

    def on_status_message(self, msg, time=0):
        self.status = msg

    def on_import_ascii(self):
        dlg = wx.FileDialog(self._widget, message="Choose a file", defaultDir=os.getcwd(), 
                            defaultFile="", wildcard="All Files|*.*|Projects|*.gt", style=wx.OPEN | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            ws = self.project.new(Worksheet, None, self.project.here)
            path = dlg.GetPaths()[0]
            ws.array, ws._header = import_ascii(path)
        dlg.Destroy()
 

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


    def on_quit(self):
        settings.set('script', 'history', '\n'.join(self.shell._widget.history))
        print >>sys.stderr, 'quit'
        self._widget.Destroy()

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

