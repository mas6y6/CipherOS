# Making plugins for CipherOS

Making plugins for CipherOS is very easy if you know how to do object orianted programming for Python and if you know how to build modules with the `__init__.py` class.

You can use the [Example plugin](https://github.com/mas6y6/CipherOS/tree/main/example_plugin) if you want.

# Setting up the directory structure

So the directory structure of a plugin is very similar to modules it must look something like this.

> [!IMPORTANT]
> **Your plugin name must be the folder where your plugin is located this is used later in the config. The name must be lowercase and have underscores `_` as spaces**

> [!TIP]
> **There is a `displayname` argument in the config for `pl info`**

```py
.
├── __init__.py
└── plugin.yml
```

You must have the `plugin.yml` file to get the class of the plugin.

# Setting up the configuration
The `plugin.yml` file must be filled out in order for CipherOS to determine how to find & run your plugin.

This is what your `plugin.yml` should look like
```yaml
# Don't change this
configversion: 3

# Version of your plugin
version: 1

team: ExampleTeam # If you have like a whole team of people that are working on this plugin you can specify it here

authors: # If you have a team of people that are working on this project
- Example

name: example_plugin # The name must match the folder of the plugin

displayname: "Example Plugin" # This is just the displayname of your plugin

description: I am a example plugin! # Description of your plugin

class: ExamplePlugin # This must match the class in the __init__.py file

dependencies: # Put your dependencies here, and CipherOS will download them from PyPi automatically (You can insert the url if you want to download that)
#  - requests
```

Here is what each setting does

### `configversion` *required*
Don't change the `configversion` setting this must be at latest configversion `3`.

### `version` *required*
The version of your plugin

### `team`
If you have a team or organization working on this plugin you can put it here

### `authors` *required (at least 1)*
If you want to list authors that helped you work on this plugin you can list it here. At least one is required.

### `name` *required*
**Your plugin name must be the folder where your plugin is located. This is used later in the config. The name must be lowercase and have underscores `_` as spaces**

This is the name of your plugin.
*Used a lot in CipherOS*

### `displayname`
***required for versions 1.5 and lower***

Display name of your plugin.

### `description`

Short description of what your plugin does

### `class` ***required***

The class of the plugin in the `__init__.py` file

**Must match the class name**

### `dependencies`

If your plugin has dependencies from PyPi you can specify them here and CipherOS will download them for you.
If you want a specific URL you can CipherOS can download that as well.

# Setting up the code

You need to import the `CipherAPI` and the `CipherPlugin` to be able to register commands and build a plugin.

```py
from cipher.plugins import CipherPlugin, CipherAPI
```

This will import the `CipherPlugin` class which directly talks to CipherOS and the `CipherAPI` for registering the plugin.
For the actual class you would need to make a child class of `CipherPlugin` class like this:

```py
class ExamplePlugin(CipherPlugin):
    def __init__(self, api: CipherAPI,config):
        # Call the parent constructor to initialize the plugin with the API
        super().__init__(api,config)

        # Register your plugin's commands
        self.register_commands()
```

The init class is to pass the `config` and the `api` variables to the subclass `CipherPlugin`.

## Commands

> [!WARNING]
> **Warning: The `api` has a built-in command() decorator.**
> **Please don't use this decorator as it is meant for default commands *only***

> [!IMPORTANT]
>
> **Please keep your commands in `register_commands(self)`**
> **If you put the commands as methods they will not be registered**
>
> ```py
> def register_commands(self):
>   @CipherPlugin.command()  # You can use this or @CipherPlugin.command()
>        def myexamplecommand(args):
>            print("Example")
> ```

To register commands you can use the `@CipherPlugin.command()` decorator.

```py
# Register a command called 'hello'
@CipherPlugin.command()
def hello(self,args):
    print("Hello from ExamplePlugin!")
```

The command decorator does have arguments to customize your plugin:

### `name`

By default, your command will be accessible by typing the name of the class into the command line, but if your command overrides default commands set a name for it in the decorator.
Example:
```py
CipherPlugin.command(name=["exampleName"])
```

### `helpflag` *deprecated*

This argument is deprecated.

### `desc`

Description of your command.

### `extradata` *deprecated*

This argument is deprecated.

### `alias`

Adds additional aliases to access the command via CLI.
Example: 
```py
@CipherPlugin.command(alias=["myalias_1","and_2"])
```

# Full structure of your plugin

This is what your entire plugin should look like
```py

# From example_plugin.

from cipher.plugins import CipherPlugin, CipherAPI

class ExamplePlugin(CipherPlugin):
    def __init__(self, api: CipherAPI,config):
        super().__init__(api,config)
        self.register_commands()
    
    def on_enable(self):
        print("Example Plugin enabled")
    
    def register_commands(self):
        @CipherPlugin.command()
        def hello(args):
            print("Hello from ExamplePlugin!")
        
        @CipherPlugin.command(name="goodbye")
        def goodbye(args):
            print("Goodbye from ExamplePlugin!")
```

# Plugin tools

These are tools for helping you make your plugin that is built into CipherOS.

## `cipher.parsers.ArgumentParser`

This is the custom built in `ArgumentParser` that CipherOS.

> [!IMPORTANT]
> **Please include after the `parser.parse_args()` function**
> ```py
> if parser.help_flag
>   return None
> ```
>
> **This required because when the flags (--help,-h) are passed the Help message is printed into the console.**
> **But it continues the script so this is required to kill the rest of the script**

- I will continue writing it later :D @mas6y6 12/3/24 9:40
