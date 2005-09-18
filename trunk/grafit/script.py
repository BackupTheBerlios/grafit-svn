import sys
import Image
import mingui as gui
# to get started with demo:
# - html widget
# - python code widget
# - tree widget

def on_item_activated(item):
    print item

def handler(*args, **kwds):
    print args, kwds

def main():
    gui.images.register('close', Image.open('../data/images/close.png'))
    gui.images.register_dir('../data/images/')

    win = gui.Window(title='Mingui doc/demo', size=(640, 480))
    box = gui.Box(win.place(), 'vertical')

    split = gui.Splitter(box.place(), 'horizontal')

    tree = gui.Tree(split.place(width=160), columns=['Topics'])
    root = gui.TreeNode()
    child = gui.TreeNode()
    root.append(child)
    tree.append(root)
    book = gui.Notebook(split.place())

    html = gui.Html(book.place(label='text'))
    html.SetPage('html/index.html')
    code = gui.Text(book.place(label='code'), multiline=True, text='hello!')
    demo = gui.Box(book.place(label='demo'))

    button = gui.Button(demo.place(expand=False, stretch=0), 'button')
    toggle = gui.Button(demo.place(expand=False, stretch=0), 'button', toggle=True)
    toggle.connect('toggled', handler)
    toggle.connect('clicked', handler)

    toggle.text = 'aaa'

    btn = gui.Button(box.place(stretch=0), 'Close', 
                     connect={'clicked': win.close})

    gui.run(win)

if __name__ == '__main__':
    main()
