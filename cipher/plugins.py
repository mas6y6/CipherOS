from cipher.api import CipherAPI
from yaml import YAMLObject

class CipherPlugin:
    api = None
    config = None
    name = None
    def __init__(self, api: CipherAPI, config):
        if CipherPlugin.api is None:
            CipherPlugin.api = api
        
        if CipherPlugin.config is None:
            CipherPlugin.config = config
        
        if CipherPlugin.name is None:
            CipherPlugin.name = self.__class__.__name__
        
        self.api.plugins[self.__class__.__name__] = self
        self.api.plugincommands[self.__class__.__name__] = []
    
    @classmethod
    def command(cls, name=None, helpflag="--help", desc=None, extradata=None, alias=None):
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
                "helpflag": helpflag,
                "alias":alias,
                "parentcommand":True,
                "extradata": extradata,
            }
            cls.api.plugincommands[cls.name].append(funcname)
            for i in alias:
                cls.api.commands[i] = {
                    "func": func,
                    "desc": desc,
                    "helpflag": helpflag,
                    "alias":[],
                    "parentcommand":False,
                    "extradata": extradata,
                }
                cls.api.plugincommands[cls.name].append(i)
            return func
        return decorator