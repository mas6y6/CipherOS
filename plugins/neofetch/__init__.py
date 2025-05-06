from cipher.api import CipherAPI
from cipher.parsers import ConfigParser, ArgumentParser
from cipher.plugins.plugins import CipherPlugin
import platform

class neofetch(CipherPlugin):
    def __init__(self, api:CipherAPI, config:ConfigParser):
        super().__init__(api, config)
        self.register_commands()

    def on_enable(self):
        print("neofetch enabled.")

    def on_disable(self):
        print("neofetch disabled.")
        
    def register_commands(self):
        @self.command(desc="Fetches the system infomation and prints it to the console.")
        def neofetch(argsraw:list[str]):
            parser = ArgumentParser(self.api,"Fetches the system infomation and prints it to the console.")
            parser.parse_args(argsraw)
            
            if parser.help_flag:
                return None
            print("OS: "+platform.system()+" "+platform.version()+" "+platform.machine())