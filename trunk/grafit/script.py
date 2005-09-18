import mingui as gui
import sys

def on_item_activated(item):
    print item

def main():
    win = gui.Window(title='Scripts')
    box = gui.Box(win.place(), 'vertical')
    book = gui.Notebook(box.place())

    text = gui.Text(book.place(label='text'), multiline=True, text='hello!')

    lst = gui.List(book.place(label='list'), 
                   columns=['arse', 'butt'], headers=True,
                   connect={'item-activated': on_item_activated})
    for d in [1, {'arse': 'hello', 'butt': 'earth'}, 'world']:
        lst.data.append(d)

    btn = gui.Button(box.place(stretch=0), 'Close', 
                     connect={'clicked': win.close})

    gui.run(win)

if __name__ == '__main__':
    main()
