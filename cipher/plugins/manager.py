import wheel, zipfile, tarfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api import CipherAPI

class PluginManager:
    def __init__(self,api: CipherAPI):
        api.console.print("q4")