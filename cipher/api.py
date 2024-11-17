import os, socket, tarfile, yaml, sys, socket, argparse, traceback, importlib.util, shutil
from cipher.exceptions import ExitCodes, ExitCodeError, PluginError, PluginInitializationError

class CipherAPI:
    def __init__(self):
        self.commands = {}
        self.pwd = os.getcwd()
        self.starterdir = os.getcwd()
        self.addressconnected = ""
        self.hostname = socket.gethostname()
        self.localip = socket.gethostbyname(self.hostname)
        self.currentenvironment = "COS"
        self.plugins = {}
        self.threads = {}
        sys.path.append(os.path.join(self.starterdir,"plugins"))
        
    def command(self, name=None, doc=None, desc=None, extradata={}, alias=[]):
        def decorator(func):
            funcname = name if name is not None else func.__name__
            self.commands[funcname] = {
                "func": func,
                "desc": desc,
                "doc": doc,
                "extradata": extradata,
            }
            for i in alias:
                self.commands[i] = {
                    "func": func,
                    "desc": desc,
                    "doc": doc,
                    "extradata": extradata,
                }
            return func
        return decorator
    
    def rm_command(self,name):
        self.commands.pop(name)
    
    def run(self,args):
        exc = None
        try:
            exc = self.commands[args[0]]["func"](args[1:])
        except KeyError:
            return ExitCodes.COMMANDNOTFOUND, traceback.format_exc()
        except ExitCodeError:
            return exc, traceback.format_exc()
        except IndexError:
            return ExitCodes.OTHERERROR, "This command requires arguments"
        except Exception:
            return ExitCodes.FATALERROR, traceback.format_exc()
        else:
            return ExitCodes.SUCCESS, None
    
    def load_plugin(self, filepath):
        yml_path = os.path.join(filepath, "plugin.yml")
        if not os.path.exists(yml_path):
            raise PluginInitializationError(f"'plugin.yml' not found in {filepath}")
        with open(yml_path, "r") as yml_file:
            yml = yaml.safe_load(yml_file)
        plugin_name = yml.get("name")
        plugin_class_name = yml.get("class")
        plugin_displayname = yml.get("displayname")
        if not plugin_name:
            raise PluginInitializationError(f"'name' is missing in {yml_path}")
        init_file = os.path.join(filepath, "__init__.py")
        if not os.path.exists(init_file):
            raise PluginInitializationError(f"'__init__.py' not found in {filepath}")
        spec = importlib.util.spec_from_file_location(plugin_name, init_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        plugin_class = getattr(module, plugin_class_name, None)
        if plugin_class is None:
            raise PluginInitializationError(f"Class '{plugin_class_name}' not found in {init_file}")

        plugin_class = getattr(module, plugin_class_name, None)
        if plugin_class is None:
            raise PluginInitializationError(f"Class '{plugin_class_name}' not found in {init_file}")

        plugin_instance = plugin_class(self)
        plugin_instance.on_load()
        
        print(f"Plugin '{plugin_displayname}' loaded successfully.")