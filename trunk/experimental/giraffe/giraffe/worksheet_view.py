import sys

import wx
import wx.grid as grid

from giraffe.worksheet.arrays import nan
from giraffe.worksheet import Worksheet

class TableData(grid.PyGridTableBase):
    """
    Custom data table for a wx.Grid
    """

    def __init__(self, worksheet):
        grid.PyGridTableBase.__init__(self)
        self.worksheet = worksheet
        print >>sys.stderr, 1
        self.worksheet.connect('data-changed', self.ResetView)
        print >>sys.stderr, 2

        self.normal_attr = grid.GridCellAttr()
        self.normal_attr.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        print >>sys.stderr, 3
        self._rows = self.GetNumberRows()
        print >>sys.stderr, 4
        self._cols = self.GetNumberCols()
        print >>sys.stderr, 5

 #   def GetAttr(self, row, col, kind):
 #       print >>sys.stderr, 'GetAttr', row, col, '#', kind
 #       attr = self.normal_attr
           # Re: [wxPython-users] GetAttr() destroys wxGridCellAttr
           # by Roger Binns other posts by this author
           # Dec 6 2003 5:25AM
           #
           # GridCellAttr objects *ARE* reference counted.  They are *only*
           # deleted when the reference count hits zero indicating that
           # noone is using them.

           # Due to an artifact of the wxPython wrapping, the reference
           #  count isn't increased and wx thinks it is no longer in
           #  use when it is.  Calling IncRef manually solves the problem.

#        attr.IncRef()
#        return attr

    def GetNumberRows(self):
        return self.worksheet.nrows

    def GetNumberCols(self):
        return self.worksheet.ncolumns

    def IsEmptyCell(self, row, col):
        return self.worksheet[col][row] is nan

    def GetValue(self, row, col):
        return str(self.worksheet[col][row]).replace('nan', '')

    def SetValue(self, row, col, value):
        self.worksheet[col][row] = float(value)

    def ResetView(self, view=None):
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        if view is None:
            view = self.GetView()
        
        view.BeginBatch()
        
        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(), 
             grid.GRIDTABLE_NOTIFY_ROWS_DELETED, grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(), 
             grid.GRIDTABLE_NOTIFY_COLS_DELETED, grid.GRIDTABLE_NOTIFY_COLS_APPENDED), ]:
            
            if new < current:
                msg = grid.GridTableMessage(self, delmsg, new, current-new)
                view.ProcessTableMessage(msg)
            elif new > current:
                msg = grid.GridTableMessage(self, addmsg, new-current)
                view.ProcessTableMessage(msg)
                self.UpdateValues(view)

        view.EndBatch()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

        # update the scrollbars and the displayed part of the grid
        view.AdjustScrollbars()
        view.ForceRefresh()

#        for r in range(self._cols):
#            self.SetColAttr(r, self.normal_attr)

    def UpdateValues(self, view):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = grid.GridTableMessage(self, grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        view.ProcessTableMessage(msg)

    def GetColLabelValue(self, col):
        return self.worksheet.column_names[col]

    def GetRowLabelValue(self, row):
        return str(row)


class WorksheetView(grid.Grid):
    def __init__(self, parent, worksheet):
        grid.Grid.__init__(self, parent, -1)


        self.worksheet = worksheet

        self.SetLabelFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.SetDefaultRowSize(20, False)

        table = TableData(self.worksheet)

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)

        self.Bind(grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightDown)  
#        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)    
        self.Bind(grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def OnMouseWheel(self, evt):
        print evt
        evt.Skip()

    def OnLabelLeftClick(self, evt):
        pass
#        evt.Skip()
        
    def OnRangeSelect(self, evt):
#        print evt, type(evt)
#        if evt.Selecting():
#            print >>sys.stderr, (evt.GetTopLeftCoords(), evt.GetBottomRightCoords())
        evt.Skip()

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
