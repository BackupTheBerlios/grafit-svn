import wx
import wx.py

from giraffe import Graph, Worksheet, Folder
from giraffe.signals import HasSignals
 
class ProjectExplorer(wx.Panel, HasSignals):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)

        splitter = wx.SplitterWindow(self)

        # tree control
        self.project_tree = wx.TreeCtrl(splitter, -1, 
                                        style=wx.TR_DEFAULT_STYLE|wx.TR_EDIT_LABELS|wx.SUNKEN_BORDER)
        self.project_tree.SetIndent(10)

        isz = (16,16)
        il = self.ilt = wx.ImageList(isz[0], isz[1])

        self.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        self.fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_REPORT_VIEW, wx.ART_OTHER, isz))
        self.wsidx       = il.Add(wx.Image('../data/images/stock_folder.png').ConvertToBitmap())
        self.project_tree.SetImageList(self.ilt)

        # object.id: treeitemid
        self.treeitems = {}


        # list control
        self.current_dir = wx.ListCtrl(splitter, -1,
                   style= wx.LC_LIST|wx.BORDER_SUNKEN|wx.LC_EDIT_LABELS|wx.LC_HRULES|wx.LC_SINGLE_SEL)

        self.il = wx.ImageList(16, 16)
        self.img_graph = self.il.Add(wx.Image('../data/images/graph.png').ConvertToBitmap())
        self.img_worksheet = self.il.Add(wx.Image('../data/images/worksheet.png').ConvertToBitmap())
        self.img_folder = self.il.Add(wx.Image('../data/images/stock_folder.png').ConvertToBitmap())

        self.current_dir.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        splitter.SplitHorizontally(self.project_tree, self.current_dir)
        sizer.Add(splitter, 1, wx.EXPAND)

        self.SetSizer(sizer)
        sizer.SetSizeHints(self)

        self.project_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
        self.current_dir.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)
       
        self.items = {}

    def connect_project(self, project):
        self.project = project

        self.project.connect('add-item', self.on_add_item)
        self.project.connect('remove-item', self.on_add_item)
        self.project.connect('change-current-folder', self.on_project_change_folder)
        self.project.connect('add-item', self.on_project_add_item)
        self.project.connect('remove-item', self.on_project_remove_item)

        self.root = self.project_tree.AddRoot('Project')
        self.project_tree.SetItemImage(self.root, self.fldridx, wx.TreeItemIcon_Normal)
        self.project_tree.SetItemImage(self.root, self.fldropenidx, wx.TreeItemIcon_Expanded)
        self.treeitems[project.top.id] = self.root

        def subfolders(f):
            for item in f.contents():
                if isinstance(item, Folder):
                    yield item

        from itertools import ifilter

        def all_subfolders(f):
            yield f
            for item in ifilter(lambda obj: isinstance(obj, Folder), f.contents()):
                for i in all_subfolders(item):
                    yield i

        for f in all_subfolders(project.top):
            if f != project.top:
                self.on_project_add_item(f)

        self.on_sel_changed(None, self.root)

    def disconnect_project(self):
        self.project.disconnect('add-item', self.on_add_item)
        self.project.disconnect('remove-item', self.on_add_item)
        self.project.disconnect('change-current-folder', self.on_project_change_folder)
        self.project.disconnect('add-item', self.on_project_add_item)
        self.project.disconnect('remove-item', self.on_project_remove_item)

        self.treeitems = {}
        self.project = None

        self.project_tree.DeleteAllItems()
        self.current_dir.ClearAll()
 
    def on_add_item(self, item):
        if item.parent == self.project.here:
            self.on_sel_changed(None, self.treeitems[item.parent.id])

    def on_item_activated(self, event):
        obj = self.project.here[event.GetItem().GetText()]
        if isinstance(obj, Folder):
            self.project.cd(obj)
        else:
            self.emit('activate-object', obj)

    def on_project_change_folder(self, folder):
        self.current_dir.ClearAll()
        self.items = {}
        
        for i, o in enumerate(folder.contents()):
            self.current_dir.InsertImageStringItem(0, o.name,
                            {Worksheet: self.img_worksheet,
                             Graph: self.img_graph,
                             Folder: self.img_folder}[type(o)])
            self.items[o.name] = o

        self.project_tree.SelectItem(self.treeitems[folder.id])

    def on_sel_changed(self, event, item=None):
        if item is None:
            item = event.GetItem()

        # find folder
        for k, v in self.treeitems.iteritems():
            if v == item:
                folder = self.project.items[k]
                
        self.project.cd(folder)

    def on_project_add_item(self, item):
        if isinstance(item, Folder):
            treeitem = self.project_tree.AppendItem(self.treeitems[item.parent.id], item.name)
            self.treeitems[item.id] = treeitem
            self.project_tree.SetItemImage(treeitem, self.wsidx, wx.TreeItemIcon_Normal)
            item.connect('rename', self.on_rename)
            self.project_tree.Expand(self.root)

    def on_project_remove_item(self, item):
        if type(item) == Folder:
            try:
                self.project_tree.Delete(self.treeitems[item.id])
            except KeyError:
                self.project_tree.Delete(self.treeitems[item.id[1:]])

    def on_rename(self, name, item):
        self.project_tree.SetItemText(self.treeitems[item.id], name)


class ScriptWindow(wx.py.shell.Shell):
    def __init__(self, parent):
        self.locals = {}
        wx.py.shell.Shell.__init__(self, parent, -1, locals=self.locals)

        self.push('from giraffe.worksheet.arrays import *')
        self.push('from giraffe.worksheet.arrays import *')
        self.push('from giraffe import *')

        self.setLocalShell()
        self.clear()
        self.prompt()
        self.zoom(-1)

    def connect_project(self, project):
        self.project = project
        self.locals.update({'project': project})
        self.push('project.set_dict(globals())')

    def disconnect_project(self):
        self.locals.update({'project': None})
        self.project.unset_dict()
        self.project = None


