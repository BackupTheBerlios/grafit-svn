"""
Command / Undo framework
"""

import signals

class Command(signals.HasSignals):
    """
    Abstract base class for commands.
    
    Derived classes must override do() and undo(), and optionally combine().
    A program-wide Command.command_list can be set, and commands added to it using register().

    do() and undo() are replaced with wrappers that emit the appropriate signal and return 
    self, one can then use commands in a one-liner like:

    FooCommand(param1, param2).do().register()
    """

    command_list = None

    def __init__(self):
        self.done = False
    
    def do(self):
        """
        Do whatever the command does.
        This method is replaced automatically with one that emits 'done' and returns self.
        """
        raise NotImplementedError

    def undo(self):
        """
        Undo whatever the command does.
        This method is replaced automatically with one that emits 'undone' and returns self.
        """
        raise NotImplementedError

    def combine(self, command):
        """
        Merge `command` into self. 
        Returns True if succesful, False if a combination is not possible
        """
        return False

    def register(self):
        """
        Add the command to the global command list (Command.command_list), if one has been set.
        """
        if self.command_list is None:
            raise NotImplementedError
        else:
            self.command_list.add(self)
        return self

    def _replace_do(self):
        self.real_do()
        self.done = True
        self.emit('done')
        return self

    def _replace_undo(self):
        self.real_undo()
        self.done = False
        self.emit('undone')
        return self

    class __metaclass__(type):
        def __init__(cls, name, bases, dct):
            # replace 'do' and 'undo' by their wrappers
            cls.real_do, cls.do  = cls.do, cls._replace_do
            cls.real_undo, cls.undo  = cls.undo, cls._replace_undo


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

    Commands are added to the list using add(), and removed using pop().
    The normal way of adding commands, however, is Command.register()
    You move forwards and backwards in the list using undo() and redo().
    Composite commands are used with begin_composite() and end_composite().
    """

    def __init__(self):
        self.commands = []
        self.composite =  None
        self.locked = 0

    def add(self, command):
        """
        Add a command to the command list
        """
        if self.locked != 0:
            return 

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
        """
        Remove the last command added to the list
        """
        if self.locked != 0:
            return
        com = self.commands.pop()
        self.emit('removed', command=com)
        return com

    def begin_composite(self, composite):
        """
        Begin a composite command. All commands added to the list
        until end_composite() is called will be added to `composite`
        instead of the list itself.
        """
        if self.locked != 0:
            return 
        self.composite = composite 

    def end_composite(self):
        """
        End a composite command.  The composite command
        is added to the list.
        """
        if self.locked != 0:
            return 
        ret = self.composite
        self.composite = None
        self.add(self.composite)
        return ret

    def lock(self):
        """
        Disable undo/redo from the list. 
        """
        self.locked += 1
        self.emit('locked')

    def unlock(self):
        """
        Enable undo/redo from the list. 
        """
        if self.locked == 0:
            raise IndexError, "TODO"
        self.locked -= 1
        self.emit('unlocked')

    def clear(self):
        """
        Clear the list.
        """
        while self.commands != []:
            self.pop()

    def undo(self):
        """
        Undo a a single command from the list.
        Returns True if a command was undone, False if there were no commands to undo.
        """
        for com in self.commands[::-1]:
            if com.done:
                break
        if com and com.done:
            self.lock()
            try:
                com.undo()
            finally:
                self.unlock()
            return True
        else:
            return False

    def redo(self):
        """
        Redo a a single command from the list.
        Returns True if a command was done, False if there were no commands to do.
        """
        for com in self.commands:
            if not com.done:
                break
        if com and not com.done:
            self.lock()
            try:
                com.do()
            finally:
                self.unlock()
            return True
        else:
            return False


