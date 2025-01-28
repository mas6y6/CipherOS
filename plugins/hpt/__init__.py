from cipher.cipher_aio import CipherPlugin, CipherAPI, ConfigParser
from hostprobe import *

class hpt(CipherPlugin):
    def __init__(self, api: CipherAPI, config:ConfigParser):
        super().__init__(api, config)
        self.register_commands()

    def on_enable(self):
        print("hostprobe-terminal enabled.")

    def on_disable(self):
        print("hostprobe-terminal disabled.")
   
    def register_commands(self):
        @self.command(name="hpt")
        def hpt(args):
            if args:
                netprobe(args, output=True, info=True)
            else:
                print("hostprobe terminal: the cross-platform nmap of python")