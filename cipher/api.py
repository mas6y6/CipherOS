import os, socket, tarfile, yaml, sys, socket, traceback, importlib.util, shutil, requests, zipfile, progressbar, re, colorama, platform
from cipher.exceptions import (
    ExitCodes,
    ExitCodeError,
    PluginError,
    PluginInitializationError,
)
from prompt_toolkit.completion import (
    Completer,
    Completion,
    PathCompleter,
    WordCompleter,
)
from wheel.wheelfile import WheelFile
from rich.console import Console
from cipher.parsers import ArgumentParser, ArgumentRequiredError, ParserError, ConfigParser

initialized_api = None

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
        self.debug = False
        self.completions = []
        self.console = Console()

    def command(self, name=None, helpflag="--help", desc=None, extradata={}, alias=[]):
        def decorator(func):
            funcname = name if name is not None else func.__name__
            self.commands[funcname] = {
                "func": func,
                "desc": desc,
                "helpflag": helpflag,
                "alias":alias,
                "parentcommand":True,
                "extradata": extradata,
            }
            for i in alias:
                self.commands[i] = {
                    "func": func,
                    "desc": desc,
                    "helpflag": helpflag,
                    "alias":[],
                    "parentcommand":False,
                    "extradata": extradata,
                }
            return func

        return decorator

    def rm_command(self, name):
        self.commands.pop(name)

    def run(self, args):
        exc = None
        try:
            exc = self.commands[args[0]]["func"](args[1:])
        except KeyError:
            return ExitCodes.COMMANDNOTFOUND, traceback.format_exc()
        except ExitCodeError:
            return exc, traceback.format_exc()
        except ArgumentRequiredError as e:
            return ExitCodes.ARGUMENTSREQUIRED, e
        except ParserError as e:
            return ExitCodes.ARGUMENTPARSERERROR, e
        except IndexError as e:
            return ExitCodes.OTHERERROR, f"This command requires arguments: {e}"
        except Exception:
            return ExitCodes.FATALERROR, traceback.format_exc()
        else:
            return ExitCodes.SUCCESS, None

    def _version_hash(self,version: str) -> int:
        sanitized_version = re.sub(r'[^0-9.]', '', version)
        version_digits = ''.join(c for c in sanitized_version if c.isdigit())
        return int(version_digits * 1000)

    def load_plugin(self, filepath):
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
                    self.console.print("Duplicate is newer then already enabled.\nDisabling and continuing enabling process...",style="bold bright_yellow")
                    self.disable_plugin(self.plugins[yml.name])
                    self.console.print("Continuing...")
                else:
                    self.console.print("Failed duplicate is older then already enabled.",style="bold bright_yellow")
                    return None
            
        plugin_name = yml.get("name")
        plugin_class_name = yml.get("class")
        plugin_displayname = yml.get("displayname")
        plugin_dependencies = yml.get("dependencies")
        print(f"Loading {plugin_displayname}")
        
        pm = PackageManager()
        if not plugin_dependencies == None:
            for i in plugin_dependencies:
                if not os.path.exists(os.path.join(self.starterdir, "data", "cache", "packages", i)):
                    if i.startswith("https://") or i.startswith("http://"):
                        pm.download_from_url(i)
                    else:
                        pm.download_package(i)

        if not plugin_name:
            raise PluginInitializationError(f"'name' is missing in {yml_path}")
        init_file = os.path.join(filepath, "__init__.py")
        if not os.path.exists(init_file):
            raise PluginInitializationError(f"'__init__.py' not found in {filepath}")
        spec = importlib.util.spec_from_file_location(plugin_name, init_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if self.debug:
            print(module)

        plugin_class = getattr(module, plugin_class_name, None)
        if plugin_class is None:
            raise PluginInitializationError(
                f"Class '{plugin_class_name}' not found in {init_file}"
            )

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

    def disable_plugin(self, plugin):
        print(f"Disabling {plugin.__class__.name}")
        plugin_instance = self.plugins[plugin.__class__.name]
        if hasattr(plugin_instance, "on_disable") and callable(
            plugin_instance.on_disable
        ):
            plugin_instance.on_disable()
        else:
            pass

        for i in self.plugincommands[plugin.__class__.name]:
            self.commands.pop(i)
        self.plugins.pop(plugin.__class__.name)
        self.updatecompletions()

    def updatecompletions(self):
        self.completions = []
        for i in os.listdir(self.pwd):
            self.completions.append(i)

        for i in self.commands:
            self.completions.append(i)

class PackageManager:
    def __init__(self):
        self.resolved_dependencies = set()
        self.api = initialized_api

    def _is_compatible_whl(self, filename):
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

    def download_package(self, package_name, version=None):
        base_url = "https://pypi.org/pypi"
        version_part = f"/{version}" if version else ""
        url = f"{base_url}/{package_name}{version_part}/json"
        download_dir = os.path.join(self.api.starterdir, "data", "cache", "packageswhl")
        packages_dir = os.path.join(self.api.starterdir, "data", "cache", "packages")

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

    def _download_file(self, url, path):
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
                bar.start()
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    bar.update(downloaded)
                bar.finish()

    def _extract_package(self, file_path, target_dir, filename):
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

    def _parse_dependency(self, dependency_string):
        import re
        match = re.match(r"([a-zA-Z0-9_\-.]+)(?:\[.*\])?(?:\s+\((.+)\))?", dependency_string)
        if match:
            dep_name = match.group(1).strip()
            dep_version = match.group(2)
            return dep_name, dep_version
        return dependency_string, None

    def is_package_installed(self, package_name, version=None):
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            installed_dir = os.path.join(self.api.starterdir, "data", "cache", "packages")
            package_path = os.path.join(installed_dir, package_name)
            return os.path.exists(package_path)

    def download_from_url(self,url):
        download_dir = os.path.join(self.api.starterdir, "data", "cache", "packageswhl")
        packages_dir = os.path.join(self.api.starterdir, "data", "cache", "packages")
        
        filename
        file_path = os.path.join(download_dir, filename)
        self._download_file(url, file_path)