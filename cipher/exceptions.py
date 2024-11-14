class ExitCodeError(Exception):
    pass
    
class ExitCodes:
    SUCCESS = 0
    ERROR = 1
    IMPROPERCMDUSE = 2
    PREMISSIONERROR = None
    ISSUEINPATH = 127
    FATALERROR = 130
    OUTOFRANGE = 255
    COMMANDNOTFOUND = 404
    
