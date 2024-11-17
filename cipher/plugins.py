from cipher.api import CipherAPI

class CipherPlugin:
    api = None
    def __init__(self, api: CipherAPI):
        if CipherPlugin.api is None:
            CipherPlugin.api = api
        self.on_load()
        self.api.plugins[self.__class__.__name__] = self
    
    def on_load(self):
        """Called when the plugin is loaded."""
        print(f"Plugin {self.__class__.__name__} loaded successfully!")
    
    def on_unload(self):
        """Called when the plugin is unloaded."""
        print(f"Plugin {self.__class__.__name__} unloaded successfully!")
    
    @classmethod
    def command(cls, name=None, doc=None, desc=None, extradata=None, alias=None):
        """
        A method to add commands through the plugin class using the API.
        This method is now a class method, so it can be used with `CipherPlugin.command()`.
        """
        # Use None as default values, and initialize the mutable objects inside the function
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
            # Handle any aliases
            for i in alias:
                cls.api.commands[i] = {
                    "func": func,
                    "desc": desc,
                    "doc": doc,
                    "extradata": extradata,
                }
            return func
        return decorator