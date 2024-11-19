import os, socket, tarfile, yaml, sys, socket, argparse, traceback, importlib.util, shutil, requests, zipfile, progressbar
from cipher.exceptions import ExitCodes, ExitCodeError, PluginError, PluginInitializationError
from prompt_toolkit.completion import Completer, Completion, PathCompleter, WordCompleter

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
        self.plugincommands = {}
        self.threads = {}
        self.completions = []
        
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
    
    def load_plugin(self, filepath, api):
        yml_path = os.path.join(filepath, "plugin.yml")
        if not os.path.exists(yml_path):
            raise PluginInitializationError(f"'plugin.yml' not found in {filepath}")
        with open(yml_path, "r") as yml_file:
            yml = yaml.safe_load(yml_file)
        plugin_name = yml.get("name")
        plugin_class_name = yml.get("class")
        plugin_displayname = yml.get("displayname")
        plugin_dependencies = yml.get("dependencies")
        print(f"Loading {plugin_displayname}")
        if not plugin_dependencies == None:
            for i in plugin_dependencies:
                if not os.path.exists(os.path.join(self.starterdir,"data","cache","packages",i)):
                    print("Downloading...",i)
                    self.download_package(i)
        
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

        plugin_instance = plugin_class(self,yml)
        if hasattr(plugin_instance, 'on_enable') and callable(plugin_instance.on_enable):
            plugin_instance.on_enable()
        self.updatecompletions()
    
    def disable_plugin(self,plugin):
        print(f"Disabling {plugin.__class__.__name__}")
        plugin_instance = self.plugins[plugin.__class__.__name__]
        if hasattr(plugin_instance, 'on_disable') and callable(plugin_instance.on_disable):
            plugin_instance.on_disable()
        else:
            pass
        
        for i in self.plugincommands[plugin.__class__.__name__]:
            self.commands.pop(i)
        self.plugins.pop(plugin.__class__.__name__)
        self.updatecompletions()
    
    def download_package(self, package_name, version=None):
        """
        Downloads the specified package and its dependencies from PyPI with a progress bar.

        :param package_name: Name of the PyPI package.
        :param version: Optional version of the package to download.
        """
        base_url = "https://pypi.org/pypi"
        version_part = f"/{version}" if version else ""
        url = f"{base_url}/{package_name}{version_part}/json"
        download_dir = os.path.join(self.starterdir, "data", "cache", "packageswhl")

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            releases = data.get("releases", {})
            if version:
                files = releases.get(version, [])
            else:
                latest_version = data.get("info", {}).get("version")
                files = releases.get(latest_version, [])

            if not files:
                print(f"No files found for package '{package_name}' version '{version}'.")
                return
            download_url = files[0]["url"]
            filename = download_url.split("/")[-1]

            os.makedirs(download_dir, exist_ok=True)
            file_path = os.path.join(download_dir, filename)
            print(f"Downloading {package_name}...")
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("Content-Length", 0))
            widgets = [
                f"Downloading {filename}: ",
                progressbar.Percentage(),
                " [", progressbar.Bar(), "] ",
                progressbar.DataSize(),
                " of ", progressbar.DataSize("max_value"),
                " | ETA: ", progressbar.ETA(),
            ]
            with progressbar.ProgressBar(max_value=total_size, widgets=widgets) as bar:
                with open(file_path, "wb") as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        bar.update(downloaded)

            print(f"\nDownloaded {package_name} to {file_path}")
            if file_path.endswith(".zip"):
                extract_path = os.path.join(self.starterdir, "data", "cache", "packages")
                os.makedirs(extract_path, exist_ok=True)
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(extract_path)
                print(f"Extracted {package_name} to {extract_path}")

        except requests.RequestException as e:
            print(f"Failed to download package '{package_name}': {e}")

    def updatecompletions(self):
        self.completions = []
        for i in os.listdir(self.pwd):
            self.completions.append(i)
        
        for i in self.commands:
            self.completions.append(i)