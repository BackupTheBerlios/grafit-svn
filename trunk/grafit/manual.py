import sys

import mingui as gui
from signals import HasSignals

import cElementTree as et


class ElementTreeNode(HasSignals):
    """Adapter from an Element to a Tree node"""
    def __init__(self, elem, isroot=False):
        self.element = elem

    def __iter__(self):
        for item in self.element:
            yield ElementTreeNode(item)
    
    def __str__(self): return self.element.tag
    def get_pixmap(self): return '16/folder.png'

def main():
    print >>sys.stderr, "loading...",
    gui.xml.merge('gui.xml')
    print >>sys.stderr, "ok"
    print >>sys.stderr, "building...",
    win = gui.xml.build('mainwin')
    print >>sys.stderr, "ok"

    tree = win.find('tree')
    r = ElementTreeNode(et.parse('gui.xml').getroot())
    tree.append(r)

    def hello():
        print 'hello'

    gui.commands['file-new'].connect('activated', hello)
    win.find('bouton').connect('clicked', hello)

    gui.run(win)

    
if __name__ == '__main__':
    main()
