from rich.console import Console
from typing import Callable, Any, Literal
import os, socket, traceback, re
from cipher.plugins.legacyplugins import CipherPlugin
from cipher.exceptions import ExitCodes, ArgumentRequiredError, ParserError
from cipher.custom_types import Command

class CipherAPI:
    def __init__(self):
        self.commands: dict[str, Command] = {}
        self.console = Console()
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
        except Exception as execptionreturn:
            if str(execptionreturn)[0] == "#":
                if str(execptionreturn)[0:] == "#310":
                    #Ignore command (Used when help window is displayed)
                    if self.debug:
                        self.console.print("[DEBUG] Help command exception raised",style="dim")
                    return ExitCodes.SUCCESS, ret_val
                if str(execptionreturn)[0:] == "#315":
                    #Ignore command (Used when help window is displayed)
                    if self.debug:
                        self.console.print("[DEBUG] Exception Ignored.",style="dim")
                    return ExitCodes.SUCCESS, ret_val
            else:
                if self.debug:
                    traceback.print_exc()
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

    def updatecompletions(self):
        self.completions: list[str] = []
        for i in os.listdir(self.pwd):
            self.completions.append(i)

        for i in self.commands:
            self.completions.append(i)