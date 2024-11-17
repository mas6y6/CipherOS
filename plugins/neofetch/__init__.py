from cipher.plugins import CipherAPI, CipherPlugin
import os, platform

class neofetch(CipherPlugin):
    def __init__(self, api: CipherAPI):
        super().__init__(api)
        self.plugin = CipherPlugin(api)
        self.register_commands()
        
    def register_commands(self):
        @self.plugin.api.command(name="neofetch")
        def neofetch(args):
            print(platform.system())