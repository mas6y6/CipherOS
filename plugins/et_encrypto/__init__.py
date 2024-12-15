from cipher.plugins import CipherAPI, CipherPlugin

class EntechEncrypto(CipherPlugin):
    def __init__(self, api: CipherAPI, config):
        super().__init__(api, config)
        self.register_commands()

    def on_enable(self):
        print("Entech Encrypto has been enabled.")

    def on_disable(self):
        print("Entech Encrypto has been disabled.")
   
    def register_commands(self):
        pass