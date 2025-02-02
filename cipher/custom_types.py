from dataclasses import dataclass
from typing import Callable, Any

@dataclass
class Command:
    func: Callable[[list[str]], Any]
    desc: str | None
    helpflag: str
    alias: list[str]
    extradata: dict[str, str]
    #parentcommand: bool | None