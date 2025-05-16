import wheel, zipfile, tarfile, os, yaml, shutil, typing
import importlib, importlib.util
from .exceptions import PluginInitFailed

if typing.TYPE_CHECKING:
    from api import CipherAPI

class PluginManager:
    def __init__(self,api: 'CipherAPI'):
        self.plugins = {}
        self.commands = {}
        self.api = api
    
    def _vernum_hash(self, version: str) -> int:
        parts = version.lstrip('v').split('.')
        return sum(int(part) * (10 ** (3 - i)) for i, part in enumerate(parts))
        
    def start(self) -> None:
        self.api.console.print("Building plugin cache",new_line_start=False)
        os.makedirs(os.path.join(self.api.configdir, "data", "cache","plugin_cache"),exist_ok=True)
        self.api.console.print("[bright_green]OK[/bright_green]")
        self.api.console.print("[bright_blue]Scanning Folder for plugins... [/bright_blue]",new_line_start=False)
        unloadedplugins = os.path.join(self.api.configdir,"plugins")
        self.api.console.print(f"[bright_blue]{len(os.listdir(unloadedplugins))} found[/bright_blue]")
        
        for file in os.listdir(unloadedplugins):
            self.api.console.print(f"Extracting {file}... ",new_line_start=False)
            if file.endswith(".tar.gz") and os.path.isfile(file):
                tar = tarfile.TarFile(os.path.join(self.api.configdir,"plugin",file))
                config = yaml.safe_load(tar.open("plugin.yml"))
                
                if os.path.exists(os.path.join(self.api.configdir,"data","cache","plugin_cache",config["config"]["name"])):
                    pathtemp = os.path.join(self.api.configdir,"data","cache","plugin_cache",config["config"]["name"])
                    configtemp = yaml.safe_load(os.path.join(pathtemp,"plugin.yml"))
                    
                    if self._vernum_hash(configtemp) == self._vernum_hash(config):
                        self.api.console.print("[yellow]Skipped[/yellow]")
                    elif self._vernum_hash(configtemp) > self._vernum_hash(config):
                        self.api.console.print("[yellow]Skipped[/yellow]")
                    else:
                        if os.path.exists(os.path.join(self.api.configdir, "data", "cache", "plugin_cache", config["config"]["name"])):
                            shutil.rmtree(os.path.join(self.api.configdir, "data", "cache", "plugin_cache", config["config"]["name"]))
                        extract_path = os.path.join(self.api.configdir, "data", "cache", "plugin_cache", config["config"]["name"])
                        os.makedirs(extract_path, exist_ok=True)
                        tar.extractall(path=extract_path)
                        self.api.console.print("[bright_green]OK[/bright_green]")
                else:
                    extract_path = os.path.join(self.api.configdir, "data", "cache", "plugin_cache", config["config"]["name"])
                    os.makedirs(extract_path, exist_ok=True)
                    tar.extractall(path=extract_path)
                    self.api.console.print("[bright_green]OK[/bright_green]")
                
            elif os.path.isdir(file):
                config = yaml.safe_load(os.path.join(self.api.configdir,"plugin",file,"plugin.yml"))
                
                if os.path.exists(os.path.join(self.api.configdir,"data","cache","plugin_cache",config["config"]["name"])):
                    configtemp = yaml.safe_load(os.path.join(self.api.configdir,"data","cache","plugin_cache",config["config"]["name"],"plugin.yml"))
                    
                    if self._vernum_hash(configtemp) == self._vernum_hash(config):
                        self.api.console.print("[yellow]Skipped[/yellow]")
                    elif self._vernum_hash(configtemp) > self._vernum_hash(config):
                        self.api.console.print("[yellow]Skipped[/yellow]")
                    else:
                        if os.path.exists(os.path.join(self.api.configdir, "data", "cache", "plugin_cache", config["config"]["name"])):
                            shutil.rmtree(os.path.join(self.api.configdir, "data", "cache", "plugin_cache", config["config"]["name"]))
                        dest_path = os.path.join(self.api.configdir, "data", "cache", "plugin_cache", config["config"]["name"])
                        shutil.copytree(os.path.join(self.api.configdir, "plugin", file), dest_path, dirs_exist_ok=True)
                        self.api.console.print("[bright_green]OK[/bright_green]")
                else:
                    dest_path = os.path.join(self.api.configdir, "data", "cache", "plugin_cache", config["config"]["name"])
                    shutil.copytree(os.path.join(self.api.configdir, "plugin", file), dest_path, dirs_exist_ok=True)
                    self.api.console.print("[bright_green]OK[/bright_green]")
    
        for i in os.listdir(os.path.join(self.api.configdir, "data", "cache", "plugin_cache")):
            config = yaml.safe_load(os.path.join(self.api.configdir, "data", "cache", "plugin_cache", i))
            self.api.console.print(f"Loading plugin \"{config['info']['displayname']}\"")
            try:
                path = os.path.join(self.api.configdir, "data", "cache", "plugin_cache",config["config"]["name"],"__init__.py")
                
                spec = importlib.util.spec_from_file_location(config["config"]["name"],path)
                if spec is None:
                    raise PluginInitFailed(
                        "__init__.py missing"
                    )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                plugin_class = getattr(module,config["config"]["class"],None)
                if plugin_class is None:
                    raise PluginInitFailed(
                        f"Class \"{config['config']['class']}\" missing"
                    )
                
                plugin_instance = plugin_class()
                self.plugins[config["config"]["name"]] = plugin_instance
                
            except Exception as e:
                self.api.console.print(f"[bold bright_red]Failed to load \"{config['info']['displayname']}\"\n{e}[/bold bright_red]")