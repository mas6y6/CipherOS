import os, socket, tarfile, yaml, sys, socket, argparse, traceback, importlib.util, shutil
from exceptions import ExitCodes, ExitCodeError

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
        sys.path.append(os.path.join(self.starterdir,"data","cache","plugins"))
        
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
        except Exception:
            return ExitCodes.FATALERROR, traceback.format_exc()
        else:
            return ExitCodes.SUCCESS, None
    
    def load_plugin(self, filepath):
        tarname = os.path.basename(filepath).split(".")[0]
        tar = tarfile.open(filepath, "r:gz")
        plugin_yml_path = f"{tarname}/plugin.yml"
        try:
            yml = yaml.load(tar.extractfile(plugin_yml_path), Loader=yaml.FullLoader)
        except KeyError:
            print(f"Error: {plugin_yml_path} not found in the archive.")
        
        pluginname = yml["name"]
        plugindisplayname = yml["name"]
        
        if os.path.exists(os.path.join(self.starterdir,"data","cache","plugins",tarname)):
            testyml = yaml.load(tar.extractfile(os.path.join(self.starterdir,"data","cache","plugins",tarname,"plugin.yml")), Loader=yaml.FullLoader)
            if not testyml["version"] == yml["version"]:
                print("Extracting "+plugindisplayname)
                tar.extractall(os.path.join(self.starterdir,"data","cache","plugins"))
            else:
                print(plugindisplayname+" is already extracted. Loading...")
        else:
            print("Extracting "+plugindisplayname)
            tar.extractall(os.path.join(self.starterdir,"data","cache","plugins"))
        
        plugin_module = importlib.import_module(pluginname)
        self.plugins[pluginname] = {"displayname":plugindisplayname}
    
    def clean_plugin_cache(self):
        for i in os.path.join(self.starterdir,"data","cache","plugins"):
            if i in self.plugins:
                continue
            else:
                shutil.()