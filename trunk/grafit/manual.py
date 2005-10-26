import sys
import mingui as gui
import mingui.xml
import cElementTree as xml

from signals import HasSignals

def handler(*args, **kwds):
    print args, kwds

@gui.Command.from_function('callable', 'callit', 'close', type='check')
def callable(*args, **kwds):
    print 'called!'

class ElementTreeNode(HasSignals):
    """Adapter from a folder to a Tree node"""
#    def __new__(cls, elem, **kwds):
#        if hasattr(elem, '_treenode'):
#            return elem._treenode
#        else:
#            obj = HasSignals.__new__(cls, elem, **kwds)
#            elem._treenode = obj
#            return obj

    def __init__(self, elem, isroot=False):
        self.element = elem
#        self.folder.connect('modified', self.on_modified)
#        if isroot:
#            self.folder.project.connect('add-item', self.on_modified)
#            self.folder.project.connect('remove-item', self.on_modified)
#        self.subfolders = list(self.folder.subfolders())

    def __iter__(self):
        for item in self.element:
            yield ElementTreeNode(item)
    
    def __str__(self): 
        return self.element.tag

    def get_pixmap(self): 
#        if self.folder == self.folder.project.top:
#            return 'grafit16.png'
#        else:
            return '16/folder.png'

#    def on_modified(self, item=None): 
#        subfolders = list(self.folder.subfolders())
#        if subfolders != self.subfolders:
#            self.emit('modified')
#            self.subfolders = subfolders
#
#    def rename(self, newname):
#        if newname == '':
#            return False
#        else:
#            self.folder.name = newname.encode('utf-8')
#            self.folder.project.top.emit('modified')
#            return True

#    def close(self):
#        print >>sys.stderr, 'close'
#    def open(self):

def main():
    gui.images.register_dir('../data/images/')
    res = mingui.xml.Resource('gui.xml')
    win = res.build('mainwin')
    tree = res.find('mainwin', 'tree')

    r = ElementTreeNode(xml.parse('gui.xml').getroot())

#    root = gui.TreeNode()
#    child = gui.TreeNode()
#    root.append(child)
#    tree.append(root)
    tree.append(r)

    gui.run(win)


def imain():
    gui.images.register_dir('../data/images/')

    # main window
    win = gui.Window(title='mingui.manual', size=(640, 520))
    gui.base.app.mainwin = win

    box = gui.Box(win(), 'vertical')

    split = gui.Splitter(box(), 'horizontal')
    panel = gui.Panel(split(width=100), 'left')
    tree = gui.Tree(panel(label='Topics', image='open'), columns=['Topics'])
    root = gui.TreeNode()
    child = gui.TreeNode()
    root.append(child)
    tree.append(root)

    split2 = gui.Splitter(split(), 'vertical')
    book = gui.Notebook(split2(stretch=1.))
    html = gui.Html(book(label='text'))
    html.LoadPage('test.html')
    code = gui.PythonEditor(book(label='code'))
    demo = gui.Box(book(label='demo'))

    button = gui.Button(demo(expand=False, stretch=0), 'button')
    toggle = gui.Button(demo(expand=False, stretch=0), 'button', toggle=True,
                        connect={'toggled': handler, 'clicked':handler})

    panel2 = gui.Panel(split2(width=100), 'bottom')
    btn = gui.Button(panel2(label='Command line', image='console'), 'arse')
    btn = gui.PythonShell(panel2(label='Command line', image='console'), locals())

    bar = gui.Menubar(win())
    menu = gui.Menu(bar, 'Foo')
    menu.append(callable)

    toggle.text = 'aaa'

    gui.run(win)

if __name__ == '__main__':
    main()
