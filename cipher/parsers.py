import json
from yaml import YAMLObject, safe_load
import io
import cipher.api

class ParserError(Exception):
    pass

class ArgumentRequiredError(Exception):
    pass

class Namespace:
    """Container for parsed arguments."""
    def __init__(self):
        pass

    def __repr__(self):
        return str(self.__dict__)

class ArgumentGroup:
    """Represents a group of arguments."""
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.arguments = []

    def add_argument(self, *args, **kwargs):
        self.arguments.append((args, kwargs))

class ArgumentParser:
    def __init__(self,api, description=None, include_help=True):
        self.description = description
        self._arguments = []
        self._flags = {}
        self._api = api
        self._console = api.console
        self._subcommands = {}
        self.help_flag = False
        self.include_help = include_help
        self.argument_groups = []

    def add_argument_group(self, name, description=None):
        """Adds a new argument group."""
        group = ArgumentGroup(name, description)
        self.argument_groups.append(group)
        return group

    def add_subcommand(self, name, description=None):
        """Adds a subcommand with its own ArgumentParser."""
        if name in self._subcommands:
            raise ParserError(f"Subcommand '{name}' already exists.")
        subparser = ArgumentParser(self._api, description=description)
        self._subcommands[name] = subparser
        return subparser

    def add_argument(self, name, type=str, default=None, required=False, help_text=None, action=None, aliases=None):
        """Adds an argument or flag."""
        aliases = aliases or []
        flag_names = [name] + aliases

        for flag_name in flag_names:
            if flag_name.startswith("--") or flag_name.startswith("-"):
                if flag_name in self._flags:
                    raise ValueError(f"Duplicate flag/alias: {flag_name}")
                self._flags[flag_name] = {
                    "type": type,
                    "default": default,
                    "required": required,
                    "help_text": help_text,
                    "action": action,
                    "name": name.lstrip("-"),
                }
            else:
                if any(arg["name"] == name for arg in self._arguments):
                    raise ValueError(f"Duplicate argument name: {name}")
                self._arguments.append({
                    "name": name,
                    "type": type,
                    "default": default,
                    "required": required,
                    "help_text": help_text,
                })

    def parse_args(self, args):
        """Parses the provided argument list."""
        parsed = Namespace()
        
        if "--help" in args or "-h" in args:
            self.print_help()
            self.help_flag = True
            return parsed

        if args and args[0] in self._subcommands:
            subcommand = args[0]
            subcommand_args = args[1:]
            parsed.subcommand = subcommand
            subparser = self._subcommands[subcommand]
            subcommand_namespace = subparser.parse_args(subcommand_args)

            for key, value in vars(subcommand_namespace).items():
                setattr(parsed, key, value)
            return parsed
        elif self._subcommands:
            raise ParserError("A subcommand is required. Use --help for usage information.")

        index = 0
        used_flags = set()
        for arg in self._arguments:
            if index < len(args):
                setattr(parsed, arg["name"], arg["type"](args[index]))
                index += 1
            elif arg["required"]:
                raise ArgumentRequiredError(f"Missing required argument: {arg['name']}")
            else:
                setattr(parsed, arg["name"], arg["default"])

        while index < len(args):
            arg = args[index]
            if arg in self._flags:
                flag = self._flags[arg]
                canonical_name = flag["name"]
                used_flags.add(canonical_name)

                if flag["action"] == "store_true":
                    setattr(parsed, canonical_name, True)
                else:
                    if index + 1 < len(args):
                        index += 1
                        setattr(parsed, canonical_name, flag["type"](args[index]))
                    else:
                        raise ArgumentRequiredError(f"Flag {arg} requires a value")
            else:
                raise ParserError(f"Unrecognized argument: {arg}")
            index += 1

        for flag, details in self._flags.items():
            if details["name"] not in used_flags:
                if details["action"] == "store_true":
                    setattr(parsed, details["name"], False)
                else:
                    setattr(parsed, details["name"], details["default"])

        return parsed


    def print_help(self):
        """Prints help message."""
        if self.description:
            self._console.print(self.description, style="bold bright_green")
        
        self._console.print("\nUsage:")
        
        
        if self._arguments:
            for arg in self._arguments:
                self._console.print(f"  [bold bright_blue]{arg['name']}[/bold bright_blue]  {arg['help_text'] or ''} (required={arg['required']})")
        
        seen_flags = set()
        if self.include_help:
            self._console.print(f"  [bold bright_yellow]--help, -h[/bold bright_yellow]  Opens this message")
        if self._flags:
            for flag, details in self._flags.items():
                if flag in seen_flags:
                    continue
                aliases = [alias for alias, info in self._flags.items() if info["name"] == details["name"]]
                flag_aliases = ", ".join(aliases)
                self._console.print(f"  [bold bright_yellow]{flag_aliases}[/bold bright_yellow]  {details['help_text'] or ''} (default={details['default']})")
                seen_flags.update(aliases)

        if self._subcommands:
            self._console.print("\nSubcommands:")
            for subcommand_name, subcommand_parser in self._subcommands.items():
                self._console.print(f"\n  [bold bright_magenta]{subcommand_name}[/bold bright_magenta]  {subcommand_parser.description or ''}")
                
                if subcommand_parser._arguments:
                    for arg in subcommand_parser._arguments:
                        self._console.print(f"    [bold bright_blue]{arg['name']}[/bold bright_blue]  {arg['help_text'] or ''} (required={arg['required']})")
                
                seen_flags = set()
                if subcommand_parser._flags:
                    for flag, details in subcommand_parser._flags.items():
                        if flag in seen_flags:
                            continue
                        aliases = [alias for alias, info in subcommand_parser._flags.items() if info["name"] == details["name"]]
                        flag_aliases = ", ".join(aliases)
                        self._console.print(f"    [bold bright_yellow]{flag_aliases}[/bold bright_yellow]  {details['help_text'] or ''} (default={details['default']})")
                        seen_flags.update(aliases)

class ConfigParser:
    def __init__(self, file_path: str):
        """Parser to parse for all versions of "plugin.yml"

        Args:
            file_path (str): Path to the plugin.yml file
        """
        with open(file_path, "r", encoding="utf-8") as file:
            self.yml = safe_load(file)
            self.dict = json.loads(json.dumps(self.yml))

        self.configversion = self.dict["configversion"]
        if self.configversion == 1:
            self.name = self.dict["name"]
            
            if not self.dict["displayname"]:
                self.displayname = self.dict["displayname"]
            else:
                self.displayname = self.name
            
            self.version = self.dict["version"]
            self.authors = None
            self.team = None
            self.description = None
            self.classname = self.dict["class"]
            self.dependencies = self.dict["dependencies"]
        elif self.configversion == 2:
            self.name = self.dict["name"]
            
            if not self.dict["displayname"]:
                self.displayname = self.dict["displayname"]
            else:
                self.displayname = self.name
            
            self.version = self.dict["version"]
            self.authors = self.dict["authors"]
            self.team = self.dict["team"]
            self.description = None
            self.classname = self.dict["class"]
            self.dependencies = self.dict["dependencies"]
        elif self.configversion == 3:
            self.name = self.dict["name"]
            
            if not self.dict["displayname"]:
                self.displayname = self.dict["displayname"]
            else:
                self.displayname = self.name
            
            self.version = self.dict["version"]
            self.authors = self.dict["authors"]
            self.team = self.dict["team"]
            self.description = self.dict["description"]
            self.classname = self.dict["class"]
            self.dependencies = self.dict["dependencies"]
        else:
            raise ParserError(
                f"The specified configversion \"{self.configversion}\" defined in the \"plugin.yml\" is not supported.\n"
                f"Please check the \"plugin.yml\" file or update to the latest version of CipherOS"
            )

        if isinstance(self.authors,list):
            if not len(self.authors) >= 1:
                raise ParserError("There must be one or more authors in the \"authors\" config")

    def get(self, key: str) -> str:
        """Returns a value of the specified key
        To provide support for older code of CipherOS that still use YAMLObject

        Args:
            key (str): Specified key

        Returns:
            str: Return of requested value
        """
        return self.dict[key]