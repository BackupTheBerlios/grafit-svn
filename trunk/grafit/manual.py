import sys
sys.path.append('..')
import mingui as gui

def handler(*args, **kwds):
    print args, kwds

@gui.Command.from_function('callable', 'callit', 'close', type='check')
def callable(*args, **kwds):
    print 'called!'

def main():
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
