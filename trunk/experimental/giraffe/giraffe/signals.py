"""
Signal / Slot framework
"""

class HasSignals(object):
    """Base class for an object that can emit signals"""

    def connect(self, signal, slot):
        """
        Connect a signal to a slot.  'signal' is a string, `slot` is any callable.
        """
        if not hasattr(self, 'signals'):
            self.signals = {}
        if signal not in self.signals:
            self.signals[signal] = []
        self.signals[signal].append(slot)

    def disconnect(self, signal, slot):
        """
        Disconnect a slot from a signal.
        """
        if not hasattr(self, 'signals'):
            raise NameError, "TODO"
        if signal not in self.signals:
            raise NameError, "TODO"
        if slot not in self.signals[signal]:
            raise NameError, "TODO"
        self.signals[signal].remove(slot)

    def emit(self, signal, *args, **kwds):
        """
        Emit a signal. All slots connected to the signal will be called.
        *args and **kwds are passed to the slot unmodified.
        """
#        print "SIGNAL: ", self, "emitted signal", signal
        if not hasattr(self, 'signals'):
            return
        if signal not in self.signals:
            return
        for slot in self.signals[signal]:
            slot(*args, **kwds)
