from cipher.plugins import CipherAPI, CipherPlugin

class FtpProbe(CipherPlugin):
    def __init__(self, api: CipherAPI):
        # Call the parent constructor to initialize the plugin with the API
        super().__init__(api)
        
        # Register your plugin's commands
        self.register_commands()
        
    def register_commands(self):
        """Method to register all commands for this plugin"""
        
        @CipherPlugin.api.command()
        def ftpprobe(args):
            """This command prints a friendly greeting"""
            print("Hello from ExamplePlugin!")
