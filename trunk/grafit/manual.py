import sys
import mingui as gui
import cElementTree as et

from signals import HasSignals

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
    gui.images.register_dir('../data/images/')
    gui.xml.merge('gui.xml')
    win = gui.xml.build('mainwin')

    tree = win.find('tree')
    r = ElementTreeNode(et.parse('gui.xml').getroot())
    tree.append(r)

    gui.run(win)

    
if __name__ == '__main__':
    main()
