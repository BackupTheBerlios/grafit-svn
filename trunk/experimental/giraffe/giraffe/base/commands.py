"""
Command / Undo framework
"""

import signals
import sys

class Command(signals.HasSignals):
    """
    Abstract base class for commands.
    
    Derived classes must override do() and undo(), and optionally combine().

    do() and undo() are replaced with wrappers that emit the appropriate signal.
    One can use commands in a one-liner like:

    FooCommand(param1, param2).do_and_register()
    """

    def __init__(self):
        self.done = False
    
    def do(self):
        """
        Do whatever the command does.
        This method is replaced automatically with one that emits 'done'.
        """
        raise NotImplementedError

    def undo(self):
        """
        Undo whatever the command does.
        This method is replaced automatically with one that emits 'undone'.
        """
        raise NotImplementedError

    def do_and_register(self):
        """
        Shorthand for command.do(); command_register().
        """
        ret = self.do()
        self.register()
        return ret


    def combine(self, command):
        """
        Merge `command` into self. 
        Returns True if succesful, False if a combination is not possible
        """
        return False

    def register(self):
        """
        Add the command to the global command list _command_list), if one has been set.
        """
        command_list.add(self)

    def _do_wrapper(self):
        ret = self.real_do()
        self.done = True
        self.emit('done')
        return ret

    def _undo_wrapper(self):
        ret = self.real_undo()
        self.done = False
        self.emit('undone')
        return ret

    class __metaclass__(type):
        def __init__(cls, name, bases, dct):
            # replace 'do' and 'undo' by their wrappers
            cls.real_do, cls.do  = cls.do, cls._do_wrapper
            cls.real_undo, cls.undo  = cls.undo, cls._undo_wrapper


class CompositeCommand(Command):
    """
    A list of commands treated as a single command.
    """
    def __init__(self):
        Command.__init__(self)
        self.commandlist = []

    def add(self, command):
        """
        Add a command to the list.
        """
        if len(self.commandlist) == 0:
            self.commandlist.append(command)
            return
        elif self.commandlist[-1].combine(command):
            pass
        else:
            self.commandlist.append(command)

    def do(self):
        for com in self.commandlist:
            com.real_do()

    def undo(self):
        for com in self.commandlist[::-1]:
            com.real_undo()


class CommandList(signals.HasSignals):
    """
    A command list, implementing undo/redo.
    """

    def __init__(self):
        self.commands = []
        self.composite =  None
        self.enabled = True

    def add(self, command):
        if not self.enabled:
            return 

        while len(self.commands) > 0 and not self.commands[-1].done:
            self.pop()

        if self.composite is not None:
            self.composite.add(command)
        else:
            if len(self.commands) == 0:
                self.commands.append(command)
            elif self.commands[-1].combine(command):
                pass
            else:
                self.commands.append(command)
            self.emit('added', command=command)

    def pop(self):
        if not self.enabled:
            return
        com = self.commands.pop()
        self.emit('removed', command=com)

    def begin_composite(self, composite):
        if not self.enabled:
            return 
        self.composite = composite 

    def end_composite(self):
        if not self.enabled:
            return 
        ret = self.composite
        self.composite = None
        return ret

    def disable(self):
        self.enabled = False
        self.emit('disabled')

    def enable(self):
        self.enabled = True
        self.emit('enabled')

    def clear(self):
        while self.commands != []:
            self.pop()

    def redo(self):
        for com in self.commands:
            if not com.done:
                break
        print >>sys.stderr, 'REDO:', com, [(type(c).__name__, c.done) for c in self.commands]
        if com and not com.done:
            e = self.enabled
            self.disable()
            try:
                com.do()
            finally:
                if e:
                    self.enable()
#            return True
#        else:
#            return False

    def undo(self):
        for com in self.commands[::-1]:
            if com.done:
                break
        if com and com.done:
            e = self.enabled
            self.disable()
            try:
                com.undo()
            finally:
                if e:
                    self.enable()
            print >>sys.stderr, 'UNDO:', com
#            return True
#        else:
#            return False


def command_from_methods(name, do, undo, redo=None, cleanup=None):
    def replace_init(selb, *args, **kwds):
        class CommandFromMethod(Command):
            def __init__(self):
                self.args, self.kwds = args, kwds
                self.__done = False

            def do(self):
                if not self.__done or redo is None:
                    ret = do(selb, *self.args, **self.kwds)
                    if len(ret) > 1 and isinstance(ret, tuple):
                        self.__state = ret[0]
                        ret = ret[1:]
                        if len(ret) == 1 and isinstance(ret, tuple):
                            ret = ret[0]
                    else:
                        self.__state = ret
                        ret = None
                    self.__done = True
                else:
                    return redo(selb, self.__state)
                return ret

            def undo(self):
                return undo(selb, self.__state)

            if cleanup is not None:
                def __del__(self):
                    cleanup(selb, self.__state)

        CommandFromMethod.__name__ = name
        com = CommandFromMethod()
        ret = com.do_and_register()
        return ret
    return replace_init


command_list = CommandList()
undo = command_list.undo
redo = command_list.redo
