# Command / Undo framework

from common import HasSignals

class Command(HasSignals):
    """
    Abstract base class for commands.
    
    Derived classes must override do() and undo(), and optionally combine().
    A program-wide Command.command_list can be set, and commands added to it using register().

    do() and undo() are replaced with wrappers that emit the appropriate signal and return 
    self, one can then use commands in a one-liner like:

    FooCommand(param1, param2).do().register()
    """

    command_list = None
    
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
        if command_list is None:
            raise NotImplementedError
        else:
            command_list.add(self)

    def _replace_do(self):
        self.real_do()
        self.emit('done')
        return self

    def _replace_undo(self):
        self.real_undo()
        self.emit('undone')
        return self

    class __metaclass__(type):
        def __init__(cls, name, bases, dct):
            # replace 'do' and 'undo' by their wrappers
            cls.real_do, cls.do  = cls.do, cls._replace_do
            cls.real_undo, cls.undo  = cls.undo, cls._replace_undo
 

class CommandList(HasSignals):
    pass
