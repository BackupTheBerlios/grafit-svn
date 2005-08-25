"""
Command / Undo framework
"""

import signals
import sys

class NoMoreCommandsError(Exception):
    pass

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
        This automatically emits 'done'.
        """
        raise NotImplementedError

    def undo(self):
        """
        Undo whatever the command does.
        This automatically emits 'undone'.
        """
        raise NotImplementedError

    def do_and_register(self):
        """Shorthand for command.do(); command_register()."""
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
        """Add the command to the global command list."""
        command_list.add(self)

    def _do_wrapper(self):
        """Wraps the `do` method emitting `done`"""
        ret = self.real_do()
        self.done = True
        self.emit('done')
        return ret

    def _undo_wrapper(self):
        """Wraps the `undo` method emitting `undone`"""
        ret = self.real_undo()
        self.done = False
        self.emit('undone')
        return ret

    class __metaclass__(type):
        def __init__(cls, name, bases, dct):
            # replace 'do' and 'undo' by their wrappers
            cls.real_do, cls.do  = cls.do, cls._do_wrapper
            cls.real_undo, cls.undo  = cls.undo, cls._undo_wrapper

    def __str__(self):
        return self.__class__.__name__


class CompositeCommand(Command):
    """A series of commands treated as a single command."""
    def __init__(self):
        Command.__init__(self)
        self.commandlist = []

    def add(self, command):
        """Add a command to the list."""
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
    """A command list, implementing undo/redo."""

    def __init__(self):
        self.commands = []
        self.composite =  None
        self.enabled = True

    def add(self, command):
        """Add a command to the list."""
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
        """Remove the last command from the list."""
        if not self.enabled:
            return
        com = self.commands.pop()
        self.emit('removed', command=com)

    def clear(self):
        """Empty the list."""
        while self.commands != []:
            self.pop()

    def redo(self):
        """Redo the last command that was undone."""
        com = False
        for com in self.commands:
            if not com.done:
                break
        if com and not com.done:
            e = self.enabled
            self.disable()
            try:
                com.do()
            finally:
                if e:
                    self.enable()
            self.emit('modified')
        else:
            raise NoMoreCommandsError

    def can_undo(self):
        for com in self.commands[::-1]:
            if com.done:
                return True
        return False

    def can_redo(self):
        for fom in self.commands:
            if not com.done:
                return True
        return False

    def undo(self):
        """Undo the last command that was done."""
        com = False
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
            self.emit('modified')
        else:
            raise NoMoreCommandsError

    def begin_composite(self, composite):
        """Begin a composite command.

        Commands added to the list until end_composite is called
        will be added to the composite command instead of the list.
        """
        if not self.enabled:
            return 
        self.composite = composite 

    def end_composite(self):
        """End a composite command.

        Returns the completed command."""
        if not self.enabled:
            return 
        ret = self.composite
        self.composite = None
        return ret

    def disable(self):
        """Disallow adding and removing items."""
        self.enabled = False
        self.emit('disabled')

    def enable(self):
        """Enable adding and removing items."""
        self.enabled = True
        self.emit('enabled')

class StopCommand(Exception):
    pass


def command_from_methods(name, do, undo, redo=None, cleanup=None, combine=None):
    """Create a command from a bunch of methods of another object.
    
    If a redo() method is given, it is called instead of do() if
    the command has been undone before.

    If a cleanup() method is given, it is called when the command
    object is deleted.

    The undo(), redo() and cleanup() methods are called with a single
    argument: the first return value of the do() method.
    """
    def replace_init(selb, *args, **kwds):
        class CommandFromMethod(Command):
            def __init__(self):
                self.args, self.kwds = args, kwds
                self.__done = False

            def do(self):
                if not self.__done or redo is None:
                    ret = do(selb, *self.args, **self.kwds)
                    if isinstance(ret, tuple) and len(ret) > 1:
                        self.state = ret[0]
                        ret = ret[1:]
                        if isinstance(ret, tuple) and len(ret) == 1:
                            ret = ret[0]
                    else:
                        self.state = ret
                        ret = None
                    self.__done = True
                else:
                    return redo(selb, self.state)
                return ret

            def undo(self):
                return undo(selb, self.state)

            def combine(self, cmd):
                if combine is not None:
                    return combine(self, self.state, cmd.state)
                else:
                    return False

            if cleanup is not None:
                def __del__(self):
                    cleanup(selb, self.state)

        CommandFromMethod.__name__ = name
        com = CommandFromMethod()
        try:
            ret = com.do_and_register()
            return ret
        except StopCommand:
#            print >>sys.stderr, "comand stopped"
            return None
    return replace_init


def command_from_methods2(name, do, undo, redo=None, cleanup=None, combine=None):
    """Create a command from a bunch of methods of another object.
    
    If a redo() method is given, it is called instead of do() if
    the command has been undone before.

    If a cleanup() method is given, it is called when the command
    object is deleted.
    """
    def replace_do(obj, *args, **kwds):
        class CommandFromMethod(Command):
            def __init__(self):
                self.args, self.kwds = args, kwds
                self.__done = False
                self.state = {}

            def do(self):
                if not self.__done or redo is None:
                    self.__done = True
                    return do(obj, self.state, *self.args, **self.kwds)
                else:
                    return redo(obj, self.state)

            def undo(self):
                return undo(obj, self.state)

            def combine(self, cmd):
                if combine is not None:
                    return combine(self, self.state, cmd.state)
                else:
                    return False

            if cleanup is not None:
                def __del__(self):
                    cleanup(obj, self.state)

        CommandFromMethod.__name__ = name
        com = CommandFromMethod()
        try:
            ret = com.do_and_register()
            return ret
        except StopCommand:
            return None
    return replace_do

# global command list
command_list = CommandList()
undo = command_list.undo
redo = command_list.redo
