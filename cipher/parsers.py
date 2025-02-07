from typing import Any, TYPE_CHECKING
from yaml import safe_load
import json
from cipher.exceptions import ParserError, ArgumentRequiredError
import types
from dataclasses import dataclass
if TYPE_CHECKING:
    from cipher.api import CipherAPI

class Namespace:
    """Container for parsed arguments."""
    subcommand: str
    def __init__(self) -> None:
        pass
    
    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__[name] = value

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
    def __init__(self, api:"CipherAPI", description:str|None=None, include_help:bool=True):
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

    def parse_args(self, args: list[str]) -> Namespace:
        """Parses the provided argument list."""
        parsed = Namespace()
        
        if "--help" in args or "-h" in args:
            self.print_help()
            self.help_flag = True
            return parsed

        if len(args) == 0:
            if self._subcommands:
                raise ParserError("A subcommand is required. Use --help for usage information.")
            missing_required_args = [arg.name for arg in self._arguments if arg.required]
            if missing_required_args:
                raise ArgumentRequiredError(f"Missing required arguments: {', '.join(missing_required_args)}")
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
        for arg in self._arguments:
            if index < len(args):
                if args[index].strip() == "":
                    raise ArgumentRequiredError(f"Missing required argument: {arg.name}")
                setattr(parsed, arg.name, arg.type(args[index]))
                index += 1
            elif arg.required:
                raise ArgumentRequiredError(f"Missing required argument: {arg.name}")
            else:
                setattr(parsed, arg.name, arg.default)
        
        while index < len(args):
            arg = args[index]
            if arg.strip() == "":
                index += 1
            if arg in self._flags:
                flag = self._flags[arg]
                canonical_name = flag.name
                used_flags.add(canonical_name)

                if flag.action == "store_true":
                    setattr(parsed, canonical_name, True)
                else:
                    if index + 1 < len(args):
                        index += 1
                        if args[index].strip() == "":
                            raise ArgumentRequiredError(f"Flag {arg} requires a value. Use --help for usage information.")
                        setattr(parsed, canonical_name, flag.type(args[index]))
                    else:
                        raise ArgumentRequiredError(f"Flag {arg} requires a value. Use --help for usage information.")
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
