from cipher.plugins import CipherAPI, CipherPlugin
import os, platform

class neofetch(CipherPlugin):
    def __init__(self, api: CipherAPI, config):
        super().__init__(api,config)
        self.register_commands()
        
    def register_commands(self):
        @CipherPlugin.api.command(name="neofetch")
        def neofetch(args):
            print(platform.system())