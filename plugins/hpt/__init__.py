from cipher.cipher_aio import CipherPlugin, CipherAPI, ConfigParser
from hostprobe import netprobe # type: ignore

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
        def hpt(args:list[str]):
            if len(args) == 1:
                netprobe(args[0], output=True, info=True)
            else:
                print("hostprobe terminal: the cross-platform nmap of python")