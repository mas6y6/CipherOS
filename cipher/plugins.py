from cipher.api import CipherAPI

class CipherPlugin:
    api = None
<<<<<<< HEAD
    config = None
    def __init__(self, api: CipherAPI, config):
        if CipherPlugin.api is None:
=======
    def __init__(self, api: CipherAPI):
        if CipherPlugin.api == None:
>>>>>>> 6a2a9e0970b36b6939bfc3e0ffd027228a64ae15
            CipherPlugin.api = api
        
        if CipherPlugin.config is None:
            CipherPlugin.config = config
        self.api.plugins[self.__class__.__name__] = self
    
    @classmethod
    def command(cls, name=None, doc=None, desc=None, extradata=None, alias=None):
        """
        A method to add commands through the plugin class using the API.
        This method is now a class method, so it can be used with `CipherPlugin.command()`.
        """
        if extradata is None:
            extradata = {}
        if alias is None:
            alias = []

        def decorator(func):
            funcname = name if name is not None else func.__name__
            cls.api.commands[funcname] = {
                "func": func,
                "desc": desc,
                "doc": doc,
                "extradata": extradata,
            }
            for i in alias:
                cls.api.commands[i] = {
                    "func": func,
                    "desc": desc,
                    "doc": doc,
                    "extradata": extradata,
                }
            return func
        return decorator