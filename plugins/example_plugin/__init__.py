from cipher.plugins import CipherAPI, CipherPlugin

# This structure of building 

class ExamplePlugin(CipherPlugin):
    def __init__(self, api: CipherAPI,config):
        # Call the parent constructor to initialize the plugin with the API
        super().__init__(api,config)
        
        # Register your plugin's commands
        self.register_commands()
    
    def on_enable(self):
        print("Example Plugin enabled")
    
    def register_commands(self):
        """Method to register all commands for this plugin"""
        
        # Register a command called 'hello'
        @CipherPlugin.api.command()  # This can also be done with @CipherPlugin.command()
        def hello(args):
            """This command prints a friendly greeting"""
            print("Hello from ExamplePlugin!")
        
        # Register another command called 'goodbye'
        @CipherPlugin.command(name="goodbye")  # You can use this or @CipherPlugin.command()
        def goodbye(args):
            """This command prints a farewell message"""
            print("Goodbye from ExamplePlugin!")
