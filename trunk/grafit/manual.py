import sys
sys.path.append('..')
import mingui as gui
import cElementTree as xml

def handler(*args, **kwds):
    print args, kwds



@gui.Command.from_function('callable', 'callit', 'close', type='check')
def callable(*args, **kwds):
    print 'called!'

def getf(defs, parent=None):
    cls, place, args, children = defs[0], defs[1], defs[2], defs[3:]
    print 'creating', cls.__name__
    if parent is None:
        win=  gui.app.mainwin= cls(**args)
    else:
        win = cls(parent(**place), **args)

    for child in children:
        getf(child, parent=win)
    return win

def from_element(elem, parent):
    pass

def main():
    tree = xml.parse("gui.xml")
    root = tree.getroot()

    cls = getattr(gui, root.tag)
    print cls

    for element in root:
        print element


def omain():
    gui.images.register_dir('../data/images/')
    win = getf(defs)
    gui.run(win)
    
defs = \
[ gui.Window, {}, dict(title='mingui.manual', size=(640, 520)), 
    [ gui.Box, {}, dict(orientation='vertical'),
        [ gui.Splitter, {}, dict(orientation='horizontal'),
            [ gui.Panel, dict(width=100), dict(position='left'),
                [ gui.Tree, dict(label='Topics', image='open'), dict(columns='Topics') ],
            ],
        ], 
    ],
]

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
