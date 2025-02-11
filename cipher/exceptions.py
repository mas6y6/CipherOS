class PluginError(Exception):
    pass

class PluginInitializationError(Exception):
    pass

class ExitCodes:
    SUCCESS = 0
    ERROR = 1
    IMPROPERCMDUSE = 2
    PREMISSIONERROR = None
    ISSUEINPATH = 127
    FATALERROR = 130
    OUTOFRANGE = 255
    ARGUMENTPARSERERROR = 231
    ARGUMENTSREQUIRED = 232
    COMMANDNOTFOUND = 404
    OTHERERROR = 400

class ParserError(Exception):
    """Exception raised when a parser error occurs."""
    pass

class ArgumentRequiredError(Exception):
    """Exception raised when a required argument is missing."""
    pass

class HelpFlagException(Exception):
    """Exception raised when the help flag is encountered."""
    pass