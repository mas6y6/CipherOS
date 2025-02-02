from cipher.api import CipherAPI, ConfigParser, Command
from typing import Callable, Any

class CipherPlugin:
    def __init__(self, api:CipherAPI, config:ConfigParser):     
        self.api = api
        
        self.config = config
        self.name = config.name

        if api.debug:
            print("PARSER", config.dict)

        self.api.plugins[config.name] = self
        self.api.plugincommands[config.name] = []

    #@classmethod
    def command(self, name:str|None=None, helpflag:str="--help", desc:str|None=None, extradata:dict[str, str]|None=None, aliases:list[str]|None=None):
        """
        A method to add commands through the plugin class using the API.
        This method is now a class method, so it can be used with `CipherPlugin.command()`.
        """
        if extradata is None: extradata = {}
        if aliases   is None: aliases = []

        def decorator(func:Callable[[list[str]], Any]) -> Callable[[list[str]], Any]:
            funcname = name if name is not None else func.__name__
            
            self.api.commands[funcname] = Command(func=func, desc=desc, helpflag=helpflag, alias=aliases, extradata=extradata) #parrentcommand = True

            if self.name not in self.api.plugincommands:
                self.api.plugincommands[self.name] = []
            
            self.api.plugincommands[self.name].append(funcname)

            for i in aliases:
                self.api.commands[i] = Command(func=func, desc=desc, helpflag=helpflag, alias=aliases, extradata=extradata) #parrentcommand = False
                self.api.plugincommands[self.name].append(i)

            return func
        return decorator

    def add_command(
            self,
            func:Callable[[list[str]], Any],
            name:str|None=None,
            helpflag:str="--help",
            desc:str|None=None,
            extradata:dict[str, str]|None=None,
            aliases:list[str]|None=None
        ) -> None:

        funcname = name if name is not None else func.__name__
        if extradata is None: extradata = {}
        if aliases   is None: aliases = []

        self.api.commands[funcname] = Command(func=func, desc=desc, helpflag=helpflag, alias=aliases, extradata=extradata)
        if self.name not in self.api.plugincommands: self.api.plugincommands[self.name] = []
        self.api.plugincommands[self.name].append(funcname)

        for i in aliases:
            self.api.commands[i] = Command(func=func, desc=desc, helpflag=helpflag, alias=aliases, extradata=extradata) #parrentcommand = False
            self.api.plugincommands[self.name].append(i)
