from cipher.plugins import CipherPlugin
from cipher.api import CipherAPI
from cipher.parsers import ConfigParser
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
        @CipherPlugin.command(name="hpt")
        def hpt(args):
            if args:
                netprobe(args, output=True, info=True)
            else:
                print("hostprobe terminal: the cross-platform nmap of python")