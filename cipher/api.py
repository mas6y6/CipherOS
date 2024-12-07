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
from cipher.packagemanager import PackageManager

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
        
        pm = PackageManager(self)
        if not plugin_dependencies == None:
            for i in plugin_dependencies:
                if not os.path.exists(os.path.join(self.starterdir, "data", "cache", "packages", i)):
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
