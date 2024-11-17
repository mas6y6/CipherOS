import os, socket, tarfile, yaml, sys, socket, argparse, traceback, importlib.util, shutil, requests, zipfile
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
        sys.path.append(os.path.join(self.starterdir,"data","cache","packages"))
        
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
        print(f"Loading Plugin '{plugin_displayname}'")
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

        plugin_instance = plugin_class(self)
        plugin_instance.__init__(api)
        try:
            plugin_instance.on_enable()
        except:
            print(f"{plugin_name} loaded.")
    
    def download_package(self,package_name, version=None):
        """
        Downloads the specified package from PyPI.
        
        :param package_name: Name of the PyPI package
        :param version: Optional version of the package to download
        :param download_dir: Directory to save the downloaded package
        """
        base_url = "https://pypi.org/pypi"
        version_part = f"/{version}" if version else ""
        url = f"{base_url}/{package_name}{version_part}/json"
        download_dir = os.path.join(self.starterdir,"data","cache","packageswhl")
        
        try:
            # Fetch package metadata
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Get the URL for the package file (source distribution or wheel)
            releases = data.get("releases", {})
            if version:
                files = releases.get(version, [])
            else:
                # Get the latest version
                latest_version = data.get("info", {}).get("version")
                files = releases.get(latest_version, [])

            if not files:
                print(f"No files found for package '{package_name}' version '{version}'.")
                return

            download_url = files[0]["url"]
            filename = download_url.split("/")[-1]

            os.makedirs(download_dir, exist_ok=True)
            file_path = os.path.join(download_dir, filename)

            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(self.starterdir,"data","cache","packages"))
        except requests.RequestException as e:
            print(f"Failed to download package '{package_name}': {e}")