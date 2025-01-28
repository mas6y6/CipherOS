from cipher.api import CipherAPI
from cipher.parsers import ConfigParser
from yaml import YAMLObject

class CipherPlugin:
    name = None

    def __init__(self, api:CipherAPI, config:ConfigParser): #api:CipherAPI        
        self.api = api
        
        self.config = config
        self.name = config.name

        if api.debug:
            print("PARSER", config.dict)

        self.api.plugins[config.name] = self
        self.api.plugincommands[config.name] = []

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
                "alias": alias,
                "parentcommand": True,
                "extradata": extradata,
            }

            if cls.name not in cls.api.plugincommands:
                cls.api.plugincommands[cls.name] = []
            
            cls.api.plugincommands[cls.name].append(funcname)

            for i in alias:
                cls.api.commands[i] = {
                    "func": func,
                    "desc": desc,
                    "helpflag": helpflag,
                    "alias": [],
                    "parentcommand": False,
                    "extradata": extradata,
                }
                cls.api.plugincommands[cls.name].append(i)

            return func
        return decorator
