from cipher.plugins import CipherPlugin, CipherAPI
from cipher.argumentparser import ArgumentParser
import os, platform

class neofetch(CipherPlugin):
    def __init__(self, api: CipherAPI, config):
        super().__init__(api, config)
        self.register_commands()

    def on_enable(self):
        print("neofetch enabled.")

    def on_disable(self):
        print("neofetch disabled.")
        
    def register_commands(self):
        @CipherPlugin.command(name="neofetch")
        def neofetch(argsraw):
            parser = ArgumentParser(self.api,"Fetches the system infomation and prints it to the console.")
            parser.parse_args(argsraw)
            
            if parser.help_flag:
                return None
            print("OS: "+platform.system()+" "+platform.version()+" "+platform.machine())