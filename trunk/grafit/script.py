import sys
sys.path.append('..')
import Image
import mingui as gui
# to get started with demo:
# - html widget
# - python code widget
# - tree widget

def handler(*args, **kwds):
    print args, kwds

@gui.Command.from_function('callable', 'callit', 'close', type='check')
def callable(*args, **kwds):
    print 'called!'

def main():
    gui.images.register('close', Image.open('../data/images/close.png'))
    gui.images.register_dir('../data/images/')

    win = gui.Window(title='Mingui doc/demo', size=(640, 480))
    gui.base.app.mainwin = win
    box = gui.Box(win.place(), 'vertical')

    split = gui.Splitter(box.place(), 'vertical')

    panel = gui.Panel(split.place(width=100), 'top')
    btn = gui.Button(panel.place(image='close'), 'arse')
    tree = gui.Tree(panel.place(image='open'), columns=['Topics'])
    root = gui.TreeNode()
    child = gui.TreeNode()
    root.append(child)
    tree.append(root)
    panel.toolbar.Realize()

    split2 = gui.Splitter(split.place(), 'horizontal')
    panel2 = gui.Panel(split2.place(width=100), 'left')
    btn = gui.Button(panel2.place(image='close'), 'arse')
    panel2.toolbar.Realize()

    book = gui.Notebook(split2.place())
    html = gui.Html(book.place(label='text'))
    html.SetPage('html/index.html')
    code = gui.Text(book.place(label='code'), multiline=True, text='hello!')
    demo = gui.Box(book.place(label='demo'))

    button = gui.Button(demo.place(expand=False, stretch=0), 'button')
    toggle = gui.Button(demo.place(expand=False, stretch=0), 'button', toggle=True)
    toggle.connect('toggled', handler)
    toggle.connect('clicked', handler)

    bar = gui.Menubar(win.place())
    menu = gui.Menu(bar, 'Foo')
    menu.append(callable)

    toggle.text = 'aaa'


    def on_changed():
        split.resize_child(tree, 100)
        

    btn = gui.Button(box.place(stretch=0), 'Close', 
                     connect={'clicked': win.close})
    btn = gui.Button(box.place(stretch=0), 'Change', 
                     connect={'clicked': on_changed})

    gui.run(win)

if __name__ == '__main__':
    main()
