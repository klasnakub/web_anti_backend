from inspect import stack

class ItemNotFoundException(Exception):
    """Custom exception for when an item is not found."""
    def __init__(self, message, *args):
        src = stack()[1].filename + ":" + str(stack()[1].lineno)
        msg = message 
        if args:
            msg += ", " + ", ".join(str(x) for x in args)
        print(src, self.__class__.__name__, msg)
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg

class ItemAlreadyExistsException(Exception):
    def __init__(self, message, *args):
        src = stack()[1].filename + ":" + str(stack()[1].lineno)
        msg = message
        if args:
            msg += ", " + ", ".join(str(x) for x in args)
        print(src, self.__class__.__name__, msg)
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class UnauthorizedException(Exception):
    """Custom exception for unauthorized access"""
    def __init__(self, message, *args):
        src = stack()[1].filename + ":" + str(stack()[1].lineno)
        msg = message
        if args:
            msg += ", " + ", ".join(str(x) for x in args)
        print(src, self.__class__.__name__, msg)
        super().__init__(msg)
        self.msg = msg
    
    def __str__(self):
        return self.msg
