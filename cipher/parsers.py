import types
from typing import Any
import json
from yaml import safe_load #,YAMLObject
from icecream import ic # type: ignore

class ParserError(Exception):
    pass

class ArgumentRequiredError(Exception):
    pass

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
            self.dict = json.loads(json.dumps(self.yml))

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
            authors: list[str] | None = None
            team = None
            description = None
            classname = self.dict["class"]
            dependencies = self.dict["dependencies"]
        elif configversion == 2:
            name = self.dict["name"]
            
            if not self.dict["displayname"]:
                displayname = self.dict["displayname"]
            else:
                displayname = name
            
            version = self.dict["version"]
            authors = self.dict["authors"]
            team = self.dict["team"]
            description = None
            classname = self.dict["class"]
            dependencies = self.dict["dependencies"]
        elif configversion == 3:
            name = self.dict["name"]
            
            if not self.dict["displayname"]:
                displayname = self.dict["displayname"]
            else:
                displayname = name
            
            version = self.dict["version"]
            authors = self.dict["authors"]
            team = self.dict["team"]
            description = self.dict["description"]
            classname = self.dict["class"]
            dependencies = self.dict["dependencies"]
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
            (dependencies, list) # list[str]
        ]
        types_match = ic([isinstance(variable, type_of_variable) for variable, type_of_variable in expected_type_match_list])
        if not all(types_match): raise ParserError(f"Some parsed data has incorrect types.")
        self.name: str = name
        self.displayname: str = displayname
        self.version: int = version
        self.authors: list[str] | None = authors
        self.team: str | None = team
        self.description: str | None = description
        self.classname: str = classname
        self.dependencies: list[str] = dependencies

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