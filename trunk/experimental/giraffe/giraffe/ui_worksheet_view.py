import sys

#import wx
#import wx.grid as grid

from giraffe.signals import HasSignals
from giraffe import gui

from giraffe.arrays import nan
from giraffe.worksheet import Worksheet

class TableData(HasSignals):
    def __init__(self, worksheet):
        self.worksheet = worksheet
        self.worksheet.connect('data-changed', self.on_data_changed)

    def on_data_changed(self): self.emit('modified')
    def get_n_columns(self): return self.worksheet.ncolumns
    def get_n_rows(self): return self.worksheet.nrows
    def get_column_name(self, col): return self.worksheet.column_names[col]
    def get_row_name(self, row): return str(row)
    def get_data(self, col, row): return str(self.worksheet[col][row]).replace('nan', '')

class WorksheetView(gui.Box):
    def __init__(self, parent, worksheet, **place):
        gui.Box.__init__(self, parent, 'vertical', **place)

        self.worksheet = worksheet
        tbbox = gui.Box(self, 'horizontal', stretch=0)
        self.toolbar = gui.Toolbar(tbbox, stretch=1)

        self.toolbar.append(gui.Action('New column', 'Create a new column', 
                                       self.on_new_column, 'stock_insert-columns.png'))

        self.closebar = gui.Toolbar(tbbox, stretch=0)
        self.closebar.append(gui.Action('Close', 'Close this worksheet', 
                                       self.on_close, 'remove.png'))

        self.table = gui.Table(self, TableData(self.worksheet))

    def on_new_column(self):
        pass

    def on_close(self):
        self.parent.delete(self)
#
