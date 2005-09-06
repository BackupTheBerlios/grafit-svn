import sys

#import wx
#import wx.grid as grid

from grafit.signals import HasSignals
from grafit import gui

from grafit.arrays import nan
from grafit.worksheet import Worksheet

import wx

class TableData(HasSignals):
    def __init__(self, worksheet):
        self.worksheet = worksheet
        self.worksheet.connect('data-changed', self.on_data_changed)

    def on_data_changed(self): self.emit('modified')
    def get_n_columns(self): return self.worksheet.ncolumns
    def get_n_rows(self): return self.worksheet.nrows
    def get_column_name(self, col): return self.worksheet.column_names[col]
    def label_edited(self, col, value): self.worksheet.columns[col].name = value
    def get_row_name(self, row): return str(row)
    def get_data(self, col, row): return str(self.worksheet[col][row]).replace('nan', '')
    def get_background_color(self, col): 
        if self.worksheet[col].expr != '':
            return (220, 220, 255)
        else:
            return (255, 255, 255)
    def set_data(self, col, row, value): 
        try:
            f = float(value)
            self.worksheet[col][row] = f
        except ValueError:
            try:
                self.worksheet[col] = self.worksheet.evaluate(value)
            except:
                raise


class WorksheetView(gui.Box):
    def __init__(self, parent, worksheet, **place):
        gui.Box.__init__(self, parent, 'horizontal', **place)

        self.worksheet = worksheet
        self.toolbar = gui.Toolbar(self, orientation='vertical', stretch=0)

        self.toolbar.append(gui.Action('New column', 'Create a new column', 
                                       self.on_new_column, 'stock_insert-columns.png'))
        self.toolbar.append(gui.Action('Delete column', 'Delete a column', 
                                       self.on_new_column, 'stock_delete-column.png'))
        self.toolbar.append(gui.Action('Move left', 'Move columns to the left', 
                                       self.on_new_column, 'stock_left.png'))
        self.toolbar.append(gui.Action('Move right', 'Move columns to the right', 
                                       self.on_new_column, 'stock_right.png'))

        self.table = gui.Table(self, TableData(self.worksheet))
        self.table.connect('right-clicked', self.on_right_clicked)
        self.table.connect('double-clicked', self.on_double_clicked)

        self.object = self.worksheet

    def on_new_column(self):
        self.worksheet[self.worksheet.suggest_column_name()] = [nan]*20

    def on_right_clicked(self, row, col):
        menu = gui.Menu()
        menu.append(gui.Action('Delete', 'delete', self.on_set_value, 'stock_delete.png'))
        self.clickcell = row, col
        self.table._widget.PopupMenu(menu._menu)

    def on_double_clicked(self, row, col):
        self.clickcell = row, col
        self.on_set_value()

    def on_close(self):
        self.parent.delete(self)

    def on_set_value(self):
        row, col = self.clickcell

        dlg = gui.Dialog(None)
        box = gui.Box(dlg, 'vertical', stretch=1)
        editor = gui.PythonEditor(box)
        auto = gui.Checkbox(box, 'Auto', stretch=0)
        btnbox = gui.Box(box, 'horizontal', stretch=0)
        ok = gui.Button(btnbox, 'OK', stretch=0)
        cancel = gui.Button(btnbox, 'Cancel', stretch=0)
        cancel.connect('clicked', dlg.close)
        ok.connect('clicked', dlg.close)

        expr = self.worksheet[col].expr

        auto.state = not expr == ''
        editor.text = expr

        dlg._widget.ShowModal()

        Worksheet.record = set()
        if auto.state:
            self.worksheet[col].expr = editor.text
        else:
            self.worksheet[col].expr = ''
            if editor.text.strip() != '':
                self.worksheet[col] = self.worksheet.evaluate(editor.text)
        Worksheet.record = None

        dlg._widget.Destroy()