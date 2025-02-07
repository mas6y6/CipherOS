from rich.console import Console
from typing import Callable, Any, Literal
import os, socket, traceback, re, requests, progressbar, zipfile, tarfile
from cipher.plugins import CipherPlugin
from cipher.exceptions import ExitCodes, ArgumentRequiredError, ParserError, PluginInitializationError
from cipher.parsers import ConfigParser
import importlib.util
from urllib.parse import unquote
from wheel.wheelfile import WheelFile
from cipher.custom_types import Command


class CipherAPI:
    def __init__(self):
        self.commands: dict[str, Command] = {}
        self._pwd = os.getcwd()
        self._currentenvironment = "COS"
        self.addressconnected = ""
        self._update_change_commandlineinfo()
        self.configdir = os.getcwd()
        self.hostname = socket.gethostname()
        try:
            self.localip = socket.gethostbyname(self.hostname)
        except Exception as e:
            self.console.print("[bold red]ERROR: A error occurred when getting local IP. Local IP will be set to 127.0.0.1[/bold red]")
            self.console.print(f"[red]{traceback.format_exception(e)}[/]")
            self.localip = "127.0.0.1"
        self.plugins: dict[str, CipherPlugin] = {}
        self.plugincommands: dict[str, list[str]] = {}
        self.threads = {}
        self.debug = False
        self.completions = []
        self.console = Console()
        self.command_history: list[str] = []

    @property
    def pwd(self) -> str:
        return self._pwd
    @pwd.setter
    def pwd(self, pwd:str) -> None:
        self._pwd = pwd
        self._update_change_commandlineinfo()
    @pwd.deleter
    def pwd(self) -> None:
        del self._pwd
    
    @property
    def currentenvironment(self) -> str:
        return self._currentenvironment
    @currentenvironment.setter
    def currentenvironment(self, cwd:str) -> None:
        self._currentenvironment = cwd
        self._update_change_commandlineinfo()
    @currentenvironment.deleter
    def currentenvironment(self) -> None:
        del self._currentenvironment
    
    def _update_change_commandlineinfo(self) -> None:
        self.commandlineinfo = f"{self.currentenvironment}{f" {self.addressconnected}" if self.addressconnected != "" else ""} {self.pwd}"

    def command(
            self, name:str|None=None, helpflag:str="--help", desc:str|None=None, extradata:dict[str, str]={}, aliases:list[str]=[]
        ) -> Callable[[Callable[[list[str]], Any]], Callable[[list[str]], Any]]:
        def decorator(func:Callable[[list[str]], Any]) -> Callable[[list[str]], Any]:
            funcname = name if name is not None else func.__name__
            self.commands[funcname] = Command(
                func=func,
                desc=desc,
                helpflag=helpflag,
                alias=aliases.copy(),
                extradata=extradata
            )
            for i in aliases:
                self.commands[i] = self.commands[funcname] = Command(
                    func=func,
                    desc=desc,
                    helpflag=helpflag,
                    alias=aliases.copy(),
                    extradata=extradata
                )
            return func

        return decorator
    
    def add_command(self, func:Callable[[list[str]], Any], name:str|None=None, desc:str|None=None, helpflag:str="--help", extradata:dict[str, str]={}, aliases:list[str]=[]) -> None:
        name = name if name != None else func.__name__
        self.commands[name] = Command(
                func=func,
                desc=desc,
                helpflag=helpflag,
                alias=aliases.copy(),
                extradata=extradata
            )
        for i in aliases:
            self.commands[i] = Command(
                    func=func,
                    desc=desc,
                    helpflag=helpflag,
                    alias=aliases.copy(),
                    extradata=extradata
                )

    def rm_command(self, name:str):
        self.commands.pop(name)

    def run(self, args: list[str]) -> tuple[Literal[0, 130, 231, 232, 400, 404], Any]:
        ret_val = None
        try:
            ret_val = self.commands[args[0]].func(args[1:])
            self.command_history.append(" ".join(args))
        except KeyError:
            if self.debug:
                traceback.print_exc()
            return ExitCodes.COMMANDNOTFOUND, traceback.format_exc()
        except ArgumentRequiredError as e:
            if self.debug:
                traceback.print_exc()
            return ExitCodes.ARGUMENTSREQUIRED, e
        except ParserError as e:
            if self.debug:
                traceback.print_exc()
            return ExitCodes.ARGUMENTPARSERERROR, e
        except IndexError as e:
            if self.debug:
                traceback.print_exc()
            return ExitCodes.OTHERERROR, f"Argument Indexing Failed: {e}"
        except Exception:
            return ExitCodes.FATALERROR, traceback.format_exc()
        else:
            return ExitCodes.SUCCESS, ret_val

    def _version_hash(self,version: str) -> int:
        sanitized_version = re.sub(r'[^0-9.]', '', version)
        version_digits = ''.join(c for c in sanitized_version if c.isdigit())
        return int(version_digits * 1000)
    
    def dependency_is_present(self, dependency_name:str) -> bool:
        dir_contents = os.listdir(os.path.join(self.configdir, "data", "cache", "packages"))
        for existing_package in dir_contents:
            #if existing_package.lower().startswith(dependency_name.lower()):
            if re.split("(-|=|.|\\s)", existing_package)[0].lower() == re.split("(-|=|.|\\s)", dependency_name)[0].lower():
                return True
        return False

    def load_plugin(self, filepath:str):
        yml_path = os.path.join(filepath, "plugin.yml")
        if self.debug:
            print(filepath)
        if not os.path.exists(yml_path):
            raise PluginInitializationError(f"'plugin.yml' not found in {filepath}")
        yml = ConfigParser(yml_path)
        if self.debug:
            print("PARSERINIT",yml.dict)
        
        # To handle if dupilcates are found
        if yml.name in self.plugins:
            self.console.print(f"Duplicate \"{yml.name}\" plugins found.\nResolving...",style="bold bright_yellow")
            newv = self._version_hash(str(yml.version))
            enabledv = self._version_hash(str(self.plugins[yml.name].config.version))
            if newv == enabledv:
                self.console.print("Failed duplicate has the same version hash as the one already enabled.",style="bold bright_yellow")
                return None
            else:
                if newv > enabledv:
                    self.console.print("Duplicate is newer then already enabled.\nDisabling and continuing plugin startup process...",style="bold bright_yellow")
                    self.disable_plugin(yml.name)
                    self.console.print("Continuing...")
                else:
                    self.console.print("Failed duplicate is older then already enabled.",style="bold bright_yellow")
                    return None
            
        plugin_name = yml.name
        plugin_class_name = yml.classname
        plugin_displayname = yml.displayname
        plugin_dependencies: list[str] | None = yml.dependencies
        print(f"Loading {plugin_displayname}")
        
        pm = PackageManager(self)
        if plugin_dependencies != None:
            for dependency_name in plugin_dependencies:
                if not self.dependency_is_present(dependency_name):
                    if dependency_name.startswith("https://") or dependency_name.startswith("http://"):
                        #raise NotImplementedError(f"Feature not yet implemented. Please contact the editors of this program for more detail")
                        pm.download_from_url(dependency_name)
                    else:
                        pm.download_package(dependency_name)

        if not plugin_name:
            raise PluginInitializationError(f"'name' is missing in {yml_path}")
        init_file = os.path.join(filepath, "__init__.py")
        if not os.path.exists(init_file):
            raise PluginInitializationError(f"'__init__.py' not found in {filepath}")
        spec = importlib.util.spec_from_file_location(plugin_name, init_file)
        if spec == None: raise PluginInitializationError(f"Something went wrong during import-spec generation.")
        module = importlib.util.module_from_spec(spec)
        if spec.loader == None: raise PluginInitializationError(f"Something went wrong while loading the import-spec")
        spec.loader.exec_module(module)
        if self.debug:
            print(module)

        plugin_class = getattr(module, plugin_class_name, None)
        if plugin_class is None:
            raise PluginInitializationError(
                f"Class '{plugin_class_name}' not found in {init_file}"
            )

        if self.debug:
            print(plugin_class)
        plugin_instance = plugin_class(self, yml)
        if self.debug:
            print("AFTERINIT",plugin_instance.config.dict)
        if hasattr(plugin_instance, "on_enable") and callable(
            plugin_instance.on_enable
        ):
            plugin_instance.on_enable()
        if self.debug:
            print(self.plugins)
        self.updatecompletions()
        if self.debug:
            print("\n\n")

    def disable_plugin(self, plugin_name:str):
        print(f"Disabling {plugin_name}")
        plugin_instance = self.plugins[plugin_name]
        if hasattr(plugin_instance, "on_disable") and callable(
            plugin_instance.on_disable # type: ignore
        ):
            plugin_instance.on_disable() # type: ignore
        else:
            pass

        for i in self.plugincommands[plugin_name]:
            self.commands.pop(i)
        self.plugins.pop(plugin_name)
        self.updatecompletions()

    def updatecompletions(self):
        self.completions: list[str] = []
        for i in os.listdir(self.pwd):
            self.completions.append(i)

        for i in self.commands:
            self.completions.append(i)

class PackageManager:
    def __init__(self, api:CipherAPI):
        self.resolved_dependencies: set[str] = set()
        self.api = api

    def _is_compatible_whl(self, filename:str):
        import sysconfig

        python_version = sysconfig.get_python_version()
        python_tag = f"cp{python_version.replace('.', '')}"
        platform_tag = sysconfig.get_platform().replace("-", "_").replace(".", "_")

        parts = filename.split("-")
        if len(parts) < 4 or not filename.endswith(".whl"):
            return False

        wheel_python_tag, wheel_platform_tag = parts[-3], parts[-1].replace(".whl", "")

        python_compatible = (
            python_tag in wheel_python_tag or
            "py3" in wheel_python_tag or
            "any" in wheel_python_tag
        )

        platform_compatible = (
            platform_tag in wheel_platform_tag or
            "any" in wheel_platform_tag
        )

        return python_compatible and platform_compatible
    
    def download_package_new(self, package_name:str, version:str|None=None) -> None:
        try:
            os.system(f"pip install {package_name}{'' if version == None else '=' + version}")
        except Exception as e:
            self.api.console.print(f"[ERROR] Failed to download package for {package_name}: {e}", style="bold red")

    def download_package(self, package_name:str, version:str|None=None):
        base_url = "https://pypi.org/pypi"
        version_part = f"/{version}" if version else ""
        url = f"{base_url}/{package_name}{version_part}/json"
        download_dir = os.path.join(self.api.configdir, "data", "cache", "packageswhl")
        packages_dir = os.path.join(self.api.configdir, "data", "cache", "packages")

        identifier = f"{package_name}=={version}" if version else package_name

        if identifier in self.resolved_dependencies:
            if self.api.debug:
                self.api.console.print(f"[DEBUG] Package already resolved: {identifier}", style="dim")
            return

        self.resolved_dependencies.add(identifier)

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            dependencies = data.get("info", {}).get("requires_dist", [])
            if dependencies:
                self.api.console.print(f"Resolving dependencies for {package_name}: {dependencies}", style="bold bright_yellow")
                for dep in dependencies:
                    dep_name, dep_version = self._parse_dependency(dep)
                    if dep_name and not self.is_package_installed(dep_name, dep_version):
                        self.download_package(dep_name, dep_version)

            releases = data.get("releases", {})
            if version:
                files = releases.get(version, [])
            else:
                latest_version = data.get("info", {}).get("version")
                files = releases.get(latest_version, [])

            compatible_files = sorted(
                [
                    file_info["url"]
                    for file_info in files
                    if (
                        file_info["url"].endswith(".whl") and self._is_compatible_whl(file_info["filename"])
                    ) or file_info["url"].endswith(".tar.gz")
                ],
                key=lambda url: (
                    "win" in url,
                    "macosx" in url,
                    "manylinux" in url,
                    "any" in url
                ),
                reverse=True
            )

            if self.api.debug:
                self.api.console.print(f"[DEBUG] Compatible files for {package_name}: {compatible_files}")

            if not compatible_files:
                self.api.console.print(f"[ERROR] No compatible files found for {package_name}", style="bold red")
                return

            download_url = compatible_files[0]
            filename = download_url.split("/")[-1]

            os.makedirs(download_dir, exist_ok=True)
            file_path = os.path.join(download_dir, filename)

            self._download_file(download_url, file_path)
            self._extract_package(file_path, packages_dir, filename)

        except requests.RequestException as e:
            self.api.console.print(f"[ERROR] Failed to fetch package metadata for {package_name}: {e}", style="bold red")
        except Exception as e:
            self.api.console.print(f"[ERROR] An unexpected error occurred: {e}", style="bold red")

    def _download_file(self, url:str, path:str):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("Content-Length", 0))
            with open(path, "wb") as f:
                bar = progressbar.ProgressBar(
                    maxval=total_size,
                    widgets=[
                        "Downloading: ",
                        progressbar.Percentage(),
                        " [",
                        progressbar.Bar(),
                        " ]",
                        progressbar.ETA(),
                    ],
                )
                bar.start() # type: ignore
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    bar.update(downloaded) # type: ignore
                bar.finish() # type: ignore

    def _extract_package(self, file_path:str, target_dir:str, filename:str):
        os.makedirs(target_dir, exist_ok=True)
        if filename.endswith(".zip"):
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(target_dir)
        elif filename.endswith(".whl"):
            with WheelFile(file_path, "r") as whl_ref:
                whl_ref.extractall(target_dir)
        elif filename.endswith(".tar.gz"):
            with tarfile.open(file_path, "r:gz") as tar_ref:
                tar_ref.extractall(target_dir)
        else:
            raise TypeError("Unsupported file format")

    def _parse_dependency(self, dependency_string:str) -> tuple[str, str | None]:
        import re
        match = re.match(r"([a-zA-Z0-9_\-.]+)(?:\[.*\])?(?:\s+\((.+)\))?", dependency_string)
        if match:
            dep_name = match.group(1).strip()
            dep_version = match.group(2)
            if isinstance(dep_name, str) and isinstance(dep_version, str):
                return dep_name, dep_version
        return dependency_string, None

    def is_package_installed(self, package_name:str, version:str|None=None):
        '''
        TODO: make version checks.
        '''
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            installed_dir = os.path.join(self.api.configdir, "data", "cache", "packages")
            package_path = os.path.join(installed_dir, package_name)
            return os.path.exists(package_path)

    def download_from_url(self, url:str):
        '''
        TODO: test this function, make filename-generation more reliable
        '''
        url_unquoted = unquote(url)
        download_dir = os.path.join(self.api.configdir, "data", "cache", "packageswhl")
        packages_dir = os.path.join(self.api.configdir, "data", "cache", "packages")
        
        filename: str | None = None
        if (len(url_unquoted.split("/")) <= 1) or (len(url_unquoted.split("/")[-1]) < 3):
            raise ValueError(f"Could not manage to get a filename.")
        else:
            filename = url_unquoted.split("/")[-1]
        file_path = os.path.join(download_dir, filename)
        self._download_file(url, file_path)
        self._extract_package(file_path, packages_dir, filename)