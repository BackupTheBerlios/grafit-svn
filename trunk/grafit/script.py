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

@gui.Command.from_function('callable', 'callit', 'close', type='check')
def callable(*args, **kwds):
    print 'called!'

class Panel(gui.Box):
    def __init__(self, place):
        gui.Box.__init__(self, place, 'vertical')
        self.contents = []
        self.toolbar = gui.Toolbar(self.place(stretch=0))
        self.splitter = place[0]
        self.splitter.resize_child(self, self.toolbar.size[1])

    def _add(self, widget, image=None, **opts):
        if image is not None:
            self.contents.append(widget)
            widget._command = self.callback(widget)
            self.toolbar.append(widget._command)
        gui.Box._add(self, widget, **opts)
        if image is not None:
            self.layout.Hide(widget)

    def callback(self, widget):
        @gui.Command.from_function('callable', 'callit', 'close', type='check')
        def callable(on):
            if on:
                for win in self.contents:
                    if win!=widget:
                        print 'aaaaaaa', win
                        win._command.state = False
            if on:
                self.layout.Show(widget)
                self.splitter.resize_child(self, 100+self.toolbar.size[1])
            else:
                self.layout.Hide(widget)
                self.splitter.resize_child(self, self.toolbar.size[1])
        return callable

def main():
    gui.images.register('close', Image.open('../data/images/close.png'))
    gui.images.register_dir('../data/images/')

    win = gui.Window(title='Mingui doc/demo', size=(640, 480))
    box = gui.Box(win.place(), 'vertical')

    split = gui.Splitter(box.place(), 'vertical')

    panel = Panel(split.place(width=100))
    btn = gui.Button(panel.place(image='close'), 'arse')
    tree = gui.Tree(panel.place(image='open'), columns=['Topics'])
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


    def on_changed():
    #    oldsize = tree.size
    #    tree.size = (100, oldsize[1])
    #    split._sashes[0]+= tree.size[0]-oldsize[0]
    #    split.SizeWindows()
        split.resize_child(tree, 100)
        

    btn = gui.Button(box.place(stretch=0), 'Close', 
                     connect={'clicked': win.close})
    btn = gui.Button(box.place(stretch=0), 'Change', 
                     connect={'clicked': on_changed})

    gui.run(win)

if __name__ == '__main__':
    main()
