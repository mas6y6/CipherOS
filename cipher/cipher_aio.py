'''
All-In-One cipher library, because I got sick of all the interlinked spaghetti code that makes typehinting a nighmare.
Putting everything into one file fixes all typehinting issues I had.
And to be completely honest, ~750 lines is not *that* much.
I know that split files are super cool for maintenance and stuff, but I put working typehints higher on my todo-list.
'''

import types
from typing import Any, Callable, Literal
from yaml import safe_load #,YAMLObject
from dataclasses import dataclass
import os, socket, tarfile, traceback, importlib.util, requests, zipfile, progressbar, re, json
from cipher.exceptions import (
    ExitCodes,
    PluginInitializationError,
)
from wheel.wheelfile import WheelFile
from rich.console import Console
from cipher.exceptions import ParserError, ArgumentRequiredError
from urllib.parse import unquote

'''
#########################
parser stuff
#########################
'''
class Namespace:
    """Container for parsed arguments."""
    subcommand: str
    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return str(self.__dict__)

class ArgumentGroup:
    """Represents a group of arguments."""
    def __init__(self, name:str, description:str|None=None) -> None:
        self.name = name
        self.description = description
        self.arguments: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def add_argument(self, *args:tuple[Any, ...], **kwargs:dict[str, Any]) -> None:
        self.arguments.append((args, kwargs))

class ConfigParser:
    def __init__(self, file_path: str) -> None:
        """Parser to parse for all versions of "plugin.yml"

        Args:
            file_path (str): Path to the plugin.yml file
        """
        with open(file_path, "r", encoding="utf-8") as file:
            self.yml = safe_load(file)
            self.dict: dict[str, str|list[str]|int|None] = json.loads(json.dumps(self.yml))

        configversion = self.dict["configversion"]
        if type(configversion) != int:
            raise ParserError(f"{type(configversion)=} does not match expected type (int).")
        if configversion == 1:
            name = self.dict["name"]
            
            if not self.dict["displayname"]:
                displayname = self.dict["displayname"]
            else:
                displayname = name
            
            version = self.dict["version"]
            authors = None
            team = None
            description = None
            classname = self.dict["class"]
            dependencies = self.dict.get("dependencies")
        elif configversion == 2:
            name = self.dict["name"]
            
            if not self.dict["displayname"]:
                displayname = self.dict["displayname"]
            else:
                displayname = name
            
            version = self.dict["version"]
            authors = self.dict["authors"]
            team = self.dict.get("team")
            description = None
            classname = self.dict["class"]
            dependencies = self.dict.get("dependencies")
        elif configversion == 3:
            name = self.dict["name"]
            
            if not self.dict["displayname"]:
                displayname = self.dict["displayname"]
            else:
                displayname = name
            
            version = self.dict["version"]
            authors = self.dict["authors"]
            team = self.dict.get("team")
            description = self.dict["description"]
            classname = self.dict["class"]
            dependencies = self.dict.get("dependencies")
        else:
            raise ParserError(
                f"The specified configversion \"{configversion}\" defined in the \"plugin.yml\" is not supported.\n"
                f"Please check the \"plugin.yml\" file or update to the latest version of CipherOS"
            )
        expected_type_match_list: list[tuple[Any, type|types.UnionType]] = [
            (name, str),
            (displayname, str),
            (version, int),
            (authors, None|list), # list[str] # type: ignore
            (team, None|str),
            (description, None|str),
            (classname, str),
            (dependencies, list|None) # list[str] # type: ignore
        ]
        types_match = [isinstance(variable, type_of_variable) for variable, type_of_variable in expected_type_match_list]
        if not all(types_match): raise ParserError(f"Some parsed data has incorrect types.")
        self.name: str = name # type: ignore
        self.displayname: str = displayname # type: ignore
        self.version: int = version # type: ignore
        self.authors: list[str] | None = authors # type: ignore
        self.team: str | None = team # type: ignore
        self.description: str | None = description # type: ignore
        self.classname: str = classname # type: ignore
        self.dependencies: list[str] | None = dependencies # type: ignore

        if isinstance(self.authors,list):
            if not len(self.authors) >= 1:
                raise ParserError("There must be one or more authors in the \"authors\" config")


@dataclass
class Flag:
    type: type
    default: str | None
    required: bool
    help_text: str | None
    action: str | None
    name: str

class ArgumentParser:
    def __init__(self, api:'CipherAPI', description:str|None=None, include_help:bool=True):
        self.description = description
        self._arguments: list[Flag] = []
        self._flags: dict[str, Flag] = {}
        self._api = api
        self._console = api.console
        self._subcommands: dict[str, ArgumentParser] = {}
        self.help_flag = False
        self.include_help = include_help
        self.argument_groups: list[ArgumentGroup] = []

    def add_argument_group(self, name:str, description:str|None=None):
        """Adds a new argument group."""
        group = ArgumentGroup(name, description)
        self.argument_groups.append(group)
        return group

    def add_subcommand(self, name:str, description:str|None=None):
        """Adds a subcommand with its own ArgumentParser."""
        if name in self._subcommands:
            raise ParserError(f"Subcommand '{name}' already exists.")
        subparser = ArgumentParser(self._api, description=description)
        self._subcommands[name] = subparser
        return subparser

    def add_argument(self, name:str, argtype:type=str, default:str|None=None, required:bool=False, help_text:str|None=None, action:str|None=None, aliases:list[str]|None=None):
        """Adds an argument or flag."""
        aliases = aliases or []
        flag_names = [name] + aliases

        for flag_name in flag_names:
            if flag_name.startswith("--") or flag_name.startswith("-"):
                if flag_name in self._flags:
                    raise ValueError(f"Duplicate flag/alias: {flag_name}")
                self._flags[flag_name] = Flag(
                    type=argtype,
                    default=default,
                    required=required,
                    help_text=help_text,
                    action=action,
                    name=name.lstrip("-"),
                )
            else:
                if any(arg.name == name for arg in self._arguments):
                    raise ValueError(f"Duplicate argument name: {name}")
                self._arguments.append(Flag(type=argtype, default=default, required=required, help_text=help_text, action=None, name=name))

    def parse_args(self, args:list[str]) -> Namespace:
        """Parses the provided argument list."""
        parsed = Namespace()

        if len(args) == 0: return parsed
        
        if "--help" in args or "-h" in args:
            self.print_help()
            self.help_flag = True
            return parsed

        if args[0] in self._subcommands:
            subcommand = args[0]
            subcommand_args = args[1:]
            parsed.subcommand = subcommand
            subparser = self._subcommands[subcommand]
            subcommand_namespace: Namespace = subparser.parse_args(subcommand_args)

            for key, value in vars(subcommand_namespace).items():
                setattr(parsed, key, value)
            return parsed
        elif self._subcommands:
            raise ParserError("A subcommand is required. Use --help for usage information.")

        index = 0
        used_flags: set[str] = set()
        missing_args: list[Flag] = []
        for arg in self._arguments:
            if index < len(args):
                setattr(parsed, arg.name, arg.type(args[index]))
                index += 1
            elif arg.required:
                missing_args.append(arg)
            else:
                setattr(parsed, arg.name, arg.default)
        if len(missing_args) > 0:
            error_message: str = "Missing required argument" + ("s" if len(missing_args) > 1 else "") + ": "
            error_message += " ".join(missing_args[i].name for i in range(len(missing_args)))
            raise ArgumentRequiredError(error_message)

        while index < len(args):
            arg = args[index]
            if arg in self._flags:
                flag = self._flags[arg]
                canonical_name = flag.name
                used_flags.add(canonical_name)

                if flag.action == "store_true":
                    setattr(parsed, canonical_name, True)
                else:
                    if index + 1 < len(args):
                        index += 1
                        setattr(parsed, canonical_name, flag.type(args[index]))
                    else:
                        raise ArgumentRequiredError(f"Flag {arg} requires a value")
            else:
                raise ParserError(f"Unrecognized argument: {arg}")
            index += 1

        for flag, details in self._flags.items():
            if details.name not in used_flags:
                if details.action == "store_true":
                    setattr(parsed, details.name, False)
                else:
                    setattr(parsed, details.name, details.default)

        return parsed

    def print_help(self):
        """Prints help message."""
        if self.description:
            self._console.print(self.description, style="bold bright_green")
        
        self._console.print("\nUsage:")
        
        
        if self._arguments:
            for arg in self._arguments:
                self._console.print(f"  [bold bright_blue]{arg.name}[/bold bright_blue]  {arg.help_text or ''} (required={arg.required})")
        
        seen_flags: set[str] = set()
        if self.include_help:
            self._console.print(f"  [bold bright_yellow]--help, -h[/bold bright_yellow]  Opens this message")
        if self._flags:
            for flag, details in self._flags.items():
                if flag in seen_flags:
                    continue
                aliases = [alias for alias, info in self._flags.items() if info.name == details.name]
                flag_aliases = ", ".join(aliases)
                self._console.print(f"  [bold bright_yellow]{flag_aliases}[/bold bright_yellow]  {details.help_text or ''} (default={details.default})")
                seen_flags.update(aliases)

        if self._subcommands:
            self._console.print("\nSubcommands:")
            for subcommand_name, subcommand_parser in self._subcommands.items():
                self._console.print(f"\n  [bold bright_magenta]{subcommand_name}[/bold bright_magenta]  {subcommand_parser.description or ''}")
                
                if subcommand_parser._arguments:
                    for arg in subcommand_parser._arguments:
                        self._console.print(f"    [bold bright_blue]{arg.name}[/bold bright_blue]  {arg.help_text or ''} (required={arg.required})")
                
                seen_flags = set()
                if subcommand_parser._flags:
                    for flag, details in subcommand_parser._flags.items():
                        if flag in seen_flags:
                            continue
                        aliases = [alias for alias, info in subcommand_parser._flags.items() if info.name == details.name]
                        flag_aliases = ", ".join(aliases)
                        self._console.print(f"    [bold bright_yellow]{flag_aliases}[/bold bright_yellow]  {details.help_text or ''} (default={details.default})")
                        seen_flags.update(aliases)

'''
#########################
api stuff
#########################
'''
@dataclass
class Command:
    func: Callable[[list[str]], Any]
    desc: str | None
    helpflag: str
    alias: list[str]
    extradata: dict[str, str]
    #parentcommand: bool | None

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

    def run(self, args:list[str]) -> tuple[Literal[0, 130, 231, 232, 400, 404], Any]:
        ret_val = None
        try:
            ret_val = self.commands[args[0]].func(args[1:])
            self.command_history.append(" ".join(args))
        except KeyError:
            return ExitCodes.COMMANDNOTFOUND, traceback.format_exc()
        except ArgumentRequiredError as e:
            return ExitCodes.ARGUMENTSREQUIRED, e
        except ParserError as e:
            return ExitCodes.ARGUMENTPARSERERROR, e
        except IndexError as e:
            return ExitCodes.OTHERERROR, f"This command requires arguments: {e}"
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

'''
#########################
plugin stuff
#########################
'''
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
