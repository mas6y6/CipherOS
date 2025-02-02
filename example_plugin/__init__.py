from cipher.api import CipherAPI
from cipher.parsers import ConfigParser
from cipher.plugins import CipherPlugin

# This structure of a plugin 

class ExamplePlugin(CipherPlugin):
    def __init__(self, api: CipherAPI, config:ConfigParser):
        # Call the parent constructor to initialize the plugin with the API
        super().__init__(api, config)
        
        # Register your plugin's commands
        self.register_commands()
    
    def on_enable(self):
        print("Example Plugin enabled")
    
    def register_commands(self):
        @self.command()
        def hello(args:list[str]):
            """This command prints a friendly greeting"""
            print("Hello from ExamplePlugin!")
        
        # Register another command called 'goodbye'
        @self.command(name="goodbye")
        def goodbye(args:list[str]):
            """This command prints a farewell message"""
            print("Goodbye from ExamplePlugin!")
