
class OpenGLWidget(Widget):
    def __init__(self, parent, **place):
        self._widget = wx.glcanvas.GLCanvas(parent._widget, -1, style=wx.glcanvas.WX_GL_DOUBLEBUFFER)
#        , attribList =[wx.glcanvas.WX_GL_DOUBLEBUFFER])
        Widget.__init__(self, parent, **place)

        self.init = False

        self._widget.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self._widget.Bind(wx.EVT_SIZE, self.OnSize)
        self._widget.Bind(wx.EVT_PAINT, self.OnPaint)
        
        for event in (wx.EVT_LEFT_DOWN, wx.EVT_MIDDLE_DOWN, wx.EVT_RIGHT_DOWN):
            self._widget.Bind(event, self.OnMouseDown)
        for event in (wx.EVT_LEFT_UP, wx.EVT_MIDDLE_UP, wx.EVT_RIGHT_UP):
            self._widget.Bind(event, self.OnMouseUp)
        for event in (wx.EVT_LEFT_DCLICK, wx.EVT_MIDDLE_DCLICK, wx.EVT_RIGHT_DCLICK):
            self._widget.Bind(event, self.OnMouseDoubleClicked)
        self._widget.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self._lastsize = (-1, -1)

        self._widget.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)    

#        self.SetCursor(wx.CROSS_CURSOR)

    def OnKeyDown(self, evt):
        self.emit('key-down', evt.GetKeyCode())
        evt.Skip()

    def redraw(self):
        self._widget.Refresh(False)

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def InitGL(self):
        self.emit('initialize-gl')
        self._widget.SwapBuffers()

    def OnSize(self, event):
#        self.emit('resize-gl', *event.GetSize())
        pass

    def OnPaint(self, event):
#        dc = wx.PaintDC(self._widget)
        self._widget.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        size = self._widget.GetSize()
        if size[0] <= 0 or size[1] <= 0:
            return
        if self._lastsize != size:
            self.emit('resize-gl', *size)
            self._lastsize = size
        self.emit('paint-gl', *size)
        self._widget.SwapBuffers()

    def OnMouseDown(self, evt):
#        self._widget.CaptureMouse()
        x, y = evt.GetPosition()
        btn = {wx.MOUSE_BTN_LEFT:1, wx.MOUSE_BTN_MIDDLE:2, wx.MOUSE_BTN_RIGHT:3}[evt.GetButton()]
        self.emit('button-pressed', x, y, btn)

    def OnMouseUp(self, evt):
#        self._widget.ReleaseMouse()
        x, y = evt.GetPosition()
        btn = {wx.MOUSE_BTN_LEFT:1, wx.MOUSE_BTN_MIDDLE:2, wx.MOUSE_BTN_RIGHT:3}[evt.GetButton()]
        self.emit('button-released', x, y, btn)

    def OnMouseDoubleClicked(self, evt):
        x, y = evt.GetPosition()
        btn = {wx.MOUSE_BTN_LEFT:1, wx.MOUSE_BTN_MIDDLE:2, wx.MOUSE_BTN_RIGHT:3}[evt.GetButton()]
        self.emit('button-doubleclicked', x, y, btn)

    def OnMouseMotion(self, evt):
        x, y = evt.GetPosition()
        self.emit('mouse-moved', x, y, evt.Dragging())

