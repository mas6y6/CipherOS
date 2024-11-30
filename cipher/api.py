import os, socket, tarfile, yaml, sys, socket, argparse, traceback, importlib.util, shutil, requests, zipfile, progressbar, re, colorama
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
from cipher.argumentparser import ArgumentParser, ArgumentRequiredError, ParserError

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

    def load_plugin(self, filepath):
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
                if not os.path.exists(
                    os.path.join(self.starterdir, "data", "cache", "packages", i)
                ):
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
            raise PluginInitializationError(
                f"Class '{plugin_class_name}' not found in {init_file}"
            )

        plugin_class = getattr(module, plugin_class_name, None)
        if plugin_class is None:
            raise PluginInitializationError(
                f"Class '{plugin_class_name}' not found in {init_file}"
            )

        plugin_instance = plugin_class(self, yml)
        if hasattr(plugin_instance, "on_enable") and callable(
            plugin_instance.on_enable
        ):
            plugin_instance.on_enable()
        self.updatecompletions()

    def disable_plugin(self, plugin):
        print(f"Disabling {plugin.__class__.__name__}")
        plugin_instance = self.plugins[plugin.__class__.__name__]
        if hasattr(plugin_instance, "on_disable") and callable(
            plugin_instance.on_disable
        ):
            plugin_instance.on_disable()
        else:
            pass

        for i in self.plugincommands[plugin.__class__.__name__]:
            self.commands.pop(i)
        self.plugins.pop(plugin.__class__.__name__)
        self.updatecompletions()

    def download_package(self, package_name, version=None):
        """
        Downloads the specified package from PyPI, resolving dependencies recursively.

        :param package_name: Name of the PyPI package.
        :param version: Optional version of the package to download.
        """
        base_url = "https://pypi.org/pypi"
        version_part = f"/{version}" if version else ""
        url = f"{base_url}/{package_name}{version_part}/json"
        download_dir = os.path.join(self.starterdir, "data", "cache", "packageswhl")
        packages_dir = os.path.join(self.starterdir, "data", "cache", "packages")

        try:
            # Fetch package metadata
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Resolve dependencies
            dependencies = data.get("info", {}).get("requires_dist", [])
            if dependencies:
                print(
                    f"Resolving dependencies for "
                    + colorama.Fore.YELLOW
                    + package_name
                    + ": "
                    + colorama.Fore.LIGHTBLUE_EX
                    + f"{dependencies}"
                    + colorama.Fore.RESET
                )
                for dep in dependencies:
                    dep_name, dep_version = self._parse_dependency(dep)
                    if dep_name and not self.is_package_installed(
                        dep_name, dep_version
                    ):
                        self.download_package(dep_name, dep_version)  # Recursive call
            releases = data.get("releases", {})
            if version:
                files = releases.get(version, [])
            else:
                latest_version = data.get("info", {}).get("version")
                files = releases.get(latest_version, [])

            if not files:
                print(
                    colorama.Fore.RED
                    + colorama.Style.BRIGHT
                    + f"No files found for package '{package_name}' version '{version}'."
                    + colorama.Fore.RESET
                    + colorama.Style.NORMAL
                )
                return
            download_url = files[0]["url"]
            filename = download_url.split("/")[-1]

            os.makedirs(download_dir, exist_ok=True)
            file_path = os.path.join(download_dir, filename)

            print(f"Downloading {package_name} from {download_url}...")
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("Content-Length", 0))
                with open(file_path, "wb") as f:
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

            if filename.endswith(".zip"):
                os.makedirs(packages_dir, exist_ok=True)
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(packages_dir)

            elif filename.endswith(".whl"):
                with WheelFile(file_path, "r") as whl_ref:
                    whl_ref.extractall(packages_dir)
            
            elif filename.endswith(".tar.gz"):
                try:
                    temp_dir = os.path.join(download_dir, "temp_extract")
                    os.makedirs(temp_dir, exist_ok=True)

                    with tarfile.open(file_path, "r:gz") as tar_ref:
                        tar_ref.extractall(temp_dir)

                    setup_py = os.path.join(temp_dir, 'setup.py')
                    package_dir = None

                    if os.path.exists(setup_py):
                        print(f"Found setup.py in {setup_py}. Attempting to find the main package...")
                        from setuptools import find_packages
                        found_packages = find_packages(where=temp_dir)
                        if found_packages:
                            package_dir = os.path.join(temp_dir, found_packages[0])

                    if not package_dir:
                        extracted_folders = [f for f in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, f))]
                        if extracted_folders:
                            package_dir = os.path.join(temp_dir, extracted_folders[0])

                    if package_dir:
                        print(f"Found main package directory: {package_dir}")
                        for item in os.listdir(package_dir):
                            s = os.path.join(package_dir, item)
                            d = os.path.join(packages_dir, item)
                            if os.path.isdir(s):
                                shutil.copytree(s, d, dirs_exist_ok=True)
                            else:
                                shutil.copy2(s, d)

                        print(f"Package {package_name} extracted and moved to {packages_dir}")
                except (tarfile.TarError, IOError) as e:
                    RuntimeError(f"Error extracting {filename}: {e}")
                finally:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)

            else:
                raise TypeError("File format is invaild to the extracter")
        except requests.RequestException as e:
            self.console.print(f"Failed to download package '{package_name}':\n {e}",style="bold bright_red")
        
        except Exception as e:
            self.console.print(f"An error occurred while extracting/downloading '{package_name}':\n {e}",style="bold bright_red")

    def _parse_dependency(self, dependency_string):
        """
        Parse a dependency string from requires_dist into name and version.

        :param dependency_string: A dependency string from requires_dist.
        :return: A tuple of (name, version) or (name, None).
        """
        import re

        match = re.match(
            r"([a-zA-Z0-9_\-\.]+)(?:\[.*\])?(?:\s+\((.+)\))?", dependency_string
        )
        if match:
            dep_name = match.group(1).strip()
            dep_version = match.group(2)
            return dep_name, dep_version
        return dependency_string, None

    def is_package_installed(self, package_name, version=None):
        """
        Checks if a package is already downloaded and installed.

        :param package_name: Name of the package.
        :param version: Optional version of the package.
        :return: True if installed, False otherwise.
        """
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            installed_dir = os.path.join(self.starterdir, "data", "cache", "packages")
            if version:
                package_path = os.path.join(installed_dir, f"{package_name}-{version}")
            else:
                package_path = os.path.join(installed_dir, package_name)
            return os.path.exists(package_path)

    def updatecompletions(self):
        self.completions = []
        for i in os.listdir(self.pwd):
            self.completions.append(i)

        for i in self.commands:
            self.completions.append(i)
