import sys
import mingui as gui

sys.path.append("..")

from grafit.signals import HasSignals
from grafit import Project, Folder, Worksheet, Graph
from grafit.settings import DATADIR
from grafit.arrays import nan

class ProjectShell(gui.PythonShell):
    """
    The shell window.

    All objects in the current folder are accesible, as well
    as the following objects:
        project - the current project
        here - the current folder
        this - the current object
        up - the parent folder
    """

    def setup(self):
        self.run('from grafit.arrays import *')
        self.run('from grafit import *')
        self.clear()
        self.run('print "# Welcome to Grafit"')
        self.prompt()

        mainwin = self.rfind('mainwin')
        mainwin.connect('open-project', self.on_open_project)
        mainwin.connect('close-project', self.on_close_project)

    def on_open_project(self, project):
        """called when a new project is opened"""
        self.locals.update({'project': project})
        self.run('project.set_dict(globals())')

    def on_close_project(self):
        """called when the project is closed"""
        self.locals['project'].unset_dict()
        self.locals.update({'project':None})


class FolderListData(HasSignals):
    def __init__(self, folder):
        self.folder = folder
        self.update()
        self.folder.connect('modified', self.update)

    def update(self):
        self.contents = [self.folder.parent]*(self.folder!=self.folder.project.top) + \
                        list(self.folder.contents())
        self.emit('modified')

    def get(self, row, column):
        if self.contents[row] == self.folder.parent: return '../'
        return self.contents[row].name + '/'*isinstance(self.contents[row], Folder)

    def get_image(self, row):
        obj = self.contents[row]
        if isinstance(obj, Worksheet): return 'worksheet'
        elif isinstance(obj, Graph): return 'graph'
#        elif isinstance(obj, Folder): return ['folder_new', 'uptriangle-o'][obj == self.folder.parent]

    def __len__(self): return len(self.contents)

    def __getitem__(self, row): return self.contents[row]


class FolderBrowser(gui.List):
    def setup(self):
        self.rfind('mainwin').connect('open-project', self.on_open_project)
        self.rfind('mainwin').connect('close-project', self.on_close_project)

        self.connect('item-activated', self.on_activated)

    def on_open_project(self, project):
        project.connect('change-current-folder', self.cd)

    def on_close_project(self, project):
        project.disconnect('change-current-folder', self.cd)

    def on_activated(self, obj):
        if isinstance(obj, Folder):
            obj.project.cd(obj)
        else:
            gui.xml.build('worksheet-view',
                          place=gui.app.mainwin.book(label='fuck'), 
                          worksheet=obj,
                          src=globals())

    def cd(self, folder):
        self.data = FolderListData(folder)


class FolderTreeNode(HasSignals):
    """Adapter from a folder to a Tree node"""
    def __new__(cls, folder, **kwds):
        if not hasattr(folder, '_treenode'):
            folder._treenode = object.__new__(cls, folder, **kwds)
        return folder._treenode

    def __init__(self, folder, isroot=False):
        self.folder = folder
        self.folder.connect('modified', self.on_modified)
        if isroot:
            self.folder.project.connect('add-item', self.on_modified)
            self.folder.project.connect('remove-item', self.on_modified)
        self.subfolders = list(self.folder.subfolders())

    def __iter__(self):
        for item in self.folder.contents():
            if isinstance(item, Folder):
                yield FolderTreeNode(item)

    def __str__(self):
        return self.folder.name.decode('utf-8')

    def get_pixmap(self):
        return '16/folder.png'

    def on_modified(self, item=None):
        subfolders = list(self.folder.subfolders())
        if subfolders != self.subfolders:
            self.emit('modified')
            self.subfolders = subfolders

    def rename(self, newname):
        if newname == '':
            return False
        else:
            self.folder.name = newname.encode('utf-8')
            self.folder.project.top.emit('modified')
            return True

class ProjectTree(gui.Tree):
    def setup(self):
        self.rfind('mainwin').connect('open-project', self.on_open_project)
        self.rfind('mainwin').connect('close-project', self.on_open_project)

    def on_open_project(self, project):
        self.append(FolderTreeNode(project.top))
        self.connect('selected', self.on_select)
        project.connect('change-current-folder', self.on_change_folder)

    def on_close_project(self, project):
        self.clear()
        self.disconnect('selected', self.on_select)
        project.disconnect('change-current-folder', self.on_change_folder)

    def on_select(self, item):
        item.folder.project.cd(item.folder)

    def on_change_folder(self, folder):
        self.select(FolderTreeNode(folder), skip_event=True)

NORMAL_COL_BGCOLOR = (255, 255, 255)
AUTO_COL_BGCOLOR = (220, 220, 255)


class TableData(HasSignals):
    def __init__(self, worksheet):
        self.worksheet = worksheet
        self.worksheet.connect('data-changed', self.on_data_changed)

    def on_data_changed(self): self.emit('modified')
    def get_n_columns(self): return self.worksheet.ncolumns
    def get_n_rows(self): return self.worksheet.nrows
    def get_column_name(self, col): return self.worksheet.column_names[col]
    def label_edited(self, col, value): self.worksheet.columns[col].name = value
    def get_row_name(self, row): return str(row)
    def get_data(self, col, row): return str(self.worksheet[col][row]).replace(repr(nan), '')
    def get_background_color(self, col):
        return (AUTO_COL_BGCOLOR, NORMAL_COL_BGCOLOR)[self.worksheet[col].expr == '']
    def set_data(self, col, row, value):
        try:
            f = float(value)
        except ValueError:
            try:
                self.worksheet[col] = self.worksheet.evaluate(value)
            except ValueError:
                print >>sys.stderr, "error"
        else:
            self.worksheet[col][row] = f


class WorksheetView(gui.Box):
    def __init__(self, place, worksheet=None, **kwds):
        gui.Box.__init__(self, place, **kwds)
        self.worksheet = worksheet

    def setup(self):
        self.table = self.find('table')

        self.table.set_data(TableData(self.worksheet))

class MainWindow(gui.Window):
    def setup(self):
        self.book = self.find('notebook')
        self.tree = self.find('tree')
        self.shell = self.find('shell')
        self.list = self.find('lili')

        p = Project('test/pdms.gt')
        self.open_project(p)

    def open_project(self, project):
        self.project = project

        self.project.connect('remove-item', self.on_project_remove_item)
        self.project.connect('modified', lambda: self.on_project_modified(True), True)
        self.project.connect('not-modified', lambda: self.on_project_modified(False), True)

        self.emit('open-project', self.project)
    
    def close_project(self):
        self.project.disconnect('remove-item', self.on_project_remove_item)

        for signal in ['modified', 'not-modified']:
            for slot in self.project.signals[signal]:
                project.disconnect(signal, slot)

        self.emit('close-project', self.project)
        self.project = None

    def on_project_modified(self, mod):
        gui.commands['file-save'].enabled = mod

    def on_project_remove_item(self, item):
        pass


def main():
    gui.xml.merge('grafit.ui')
    gui.run(gui.xml.build('mainwin', src=globals()))

if __name__ == '__main__':
    main()
