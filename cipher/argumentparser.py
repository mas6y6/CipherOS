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


class ArgumentParser:
    def __init__(self,api, description=None):
        self.description = description
        self._arguments = []
        self._flags = {}
        self._api = api
        self._console = api.console
        self._subcommands = {}
        self.help_flag = False

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
    
    def add_subcommand(self, name, parser):
        """Adds a subcommand with its own ArgumentParser."""
        if name in self._subcommands:
            raise ParserError(f"Subcommand '{name}' already exists.")
        self._subcommands[name] = parser

    def parse_args(self, args):
        """Parses the provided argument list."""
        if "--help" in args or "-h" in args:
            self.print_help()
            self.help_flag = True
            return Namespace()
        
        if args and args[0] in self._subcommands:
            # Handle subcommands
            subcommand = args[0]
            subcommand_args = args[1:]
            return self._subcommands[subcommand].parse_args(subcommand_args)
        
        parsed = Namespace()
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
            elif arg in ("--help", "-h"):
                self.print_help()
                self.help_flag = True
                return Namespace()
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
            self._console.print(self.description,style="bold bright_green")
        self._console.print("\nUsage:")
        for arg in self._arguments:
            self._console.print(f"  [bold bright_blue]{arg['name']}[/bold bright_blue]  {arg['help_text'] or ''} (required={arg['required']})")
        seen_flags = set()
        for flag, details in self._flags.items():
            if flag in seen_flags:
                continue
            aliases = [alias for alias, info in self._flags.items() if info["name"] == details["name"]]
            flag_aliases = ", ".join(aliases)
            self._console.print(f"  [bold bright_yellow]{flag_aliases}[/bold bright_yellow]  {details['help_text'] or ''} (default={details['default']})")
            
            seen_flags.update(aliases)
        if self._subcommands:
            self._console.print("\nSubcommands:")
            for subcommand in self._subcommands:
                self._console.print(f"  [bold bright_magenta]{subcommand}[/bold bright_magenta]")