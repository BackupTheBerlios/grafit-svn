import sys

import wx
import wx.grid as grid

from giraffe.worksheet.mkarray import nan
from giraffe.worksheet import Worksheet

class TableData(grid.PyGridTableBase):
    """
    This is all it takes to make a custom data table to plug into a
    wxGrid.  There are many more methods that can be overridden, but
    the ones shown below are the required ones.  This table simply
    provides strings containing the row and column values.
    """

    def __init__(self, worksheet):
        grid.PyGridTableBase.__init__(self)
        self.worksheet = worksheet
        self.worksheet.connect('data-changed', self.on_data_changed)
        self.normal_attr = grid.GridCellAttr()
        self.normal_attr.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

        self._cached_col = None
        self._cached_data = None

    def GetAttr(self, row, col, kind):
        print >>sys.stderr, 'A', row, col
        attr = self.normal_attr
        attr.IncRef()
        return attr

    def GetNumberRows(self):
        return self.worksheet.nrows

    def GetNumberCols(self):
        return self.worksheet.ncolumns

    def IsEmptyCell(self, row, col):
        return self.worksheet[col][row] is nan

    def GetValue(self, row, col):
        print >>sys.stderr, row, col
        return str(self.worksheet[col][row]).replace('nan', '')

    def SetValue(self, row, col, value):
        self.worksheet[col][row] = float(value)

    def on_data_changed(self):
        self.ResetView(self.GetView())

    def ResetView(self, view):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        view.BeginBatch()
        
        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(), grid.GRIDTABLE_NOTIFY_ROWS_DELETED, grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(), grid.GRIDTABLE_NOTIFY_COLS_DELETED, grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
        ]:
            
            if new < current:
                msg = grid.GridTableMessage(self,delmsg,new,current-new)
                view.ProcessTableMessage(msg)
            elif new > current:
                msg = grid.GridTableMessage(self,addmsg,new-current)
                view.ProcessTableMessage(msg)
                self.UpdateValues(view)

        view.EndBatch()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()
        # update the column rendering plugins
#        self._updateColAttrs(view)

        # update the scrollbars and the displayed part of the grid
        view.AdjustScrollbars()
        view.ForceRefresh()

    def UpdateValues(self, view):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = grid.GridTableMessage(self, grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        view.ProcessTableMessage(msg)

#    def GetColLabelValue(self, col):
#        return self.worksheet.column_names[col]

#    def GetRowLabelValue(self, row):
#        return str(row)


class WorksheetView(grid.Grid):
    def __init__(self, parent, worksheet):
        grid.Grid.__init__(self, parent, -1)

        if worksheet:
            self.worksheet = worksheet
        else:
            w = Worksheet('hello', None)
            w.add_column('A')
            w.add_column('B')
            w.A = [1,2,3,4]
            w.B = [1,4,9,16]
            self.worksheet = w

        table = TableData(self.worksheet)


        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)

        self.Bind(grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightDown)  
        table.SetColAttr(0, table.normal_attr)
        table.SetColAttr(1, table.normal_attr)
#        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)    
        
    def OnKeyDown(self, evt):
        if evt.KeyCode() != wx.WXK_RETURN:
            evt.Skip()
            return
        if evt.ControlDown():   # the edit control needs this key
            evt.Skip()
            return

        self.DisableCellEditControl()

        if not self.MoveCursorDown(True): 
            # add a new row
            self.GetTable().worksheet[self.GetGridCursorCol()][self.GetTable().GetNumberRows()] = nan

    def OnRightDown(self, event):
        print "hello"
        for l in range(100):
            self.GetTable().worksheet.add_column('col'+str(l))
        self.GetTable().worksheet.A[999] = 14
        print self.GetSelectedRows()


class TestFrame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "Huge (virtual) Table Demo", size=(640,480))
        grid = WorksheetView(self)

        grid.SetReadOnly(5,5, True)

if __name__ == '__main__':
    import sys
    app = wx.PySimpleApp()
    frame = TestFrame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()
