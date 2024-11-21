import colorama, os, sys
from prompt_toolkit.completion import Completion, Completer, PathCompleter

def printerror(msg):
    print(colorama.Style.BRIGHT+colorama.Fore.RED+msg+colorama.Fore.RESET+colorama.Style.NORMAL)

def register_main_cmds(api):
    @api.command()
    class exit():
        def execute(args):
            print("Closing CipherOS")
            sys.exit(0)

    @api.command(alias=["cd"])
    class chdir():
        def execute(args):
            if os.path.isdir(args[0]):
                os.chdir(args[0])
            else:
                printerror(f"Error: {args[0]} is a file")
            api.pwd = os.getcwd()
            api.updatecompletions()

    @api.command()
    class mkdir():
        def execute(args):
            if not os.path.exists(args[0]):
                os.mkdir(args[0])
            else:
                printerror(f"Error: {args[0]} exists")

    @api.command(alias=["cls"])
    class clear():
        def execute(args):
            print("\033c", end="")

    @api.command(alias=["pl"])
    class plugins():
        def execute(args):
            if args[0] == "reloadall":
                print("Reloading all plugins")
                for i in list(api.plugins):
                    api.disable_plugin(api.plugins[i])
                for i in os.listdir(os.path.join(api.starterdir,"plugins")):
                    api.load_plugin(os.path.join(api.starterdir,"plugins",i), api)
                print("Reload complete")
            
            elif args[0] == "disable":
                api.disable_plugin(args[1])
            
            elif args[0] == "enable":
                pass
            
            elif args[0] == "list":
                pass
            
            elif args[0] == "info":
                pass

    @api.command(alias=["list","l"])
    class ls():
        def execute(args):
            if len(args) > 0:
                path = args[0]
            else:
                path = api.pwd
            try:
                raw = os.listdir(path)
            except FileNotFoundError:
                printerror(f"Error: The directory '{path}' does not exist.")
                return
            except PermissionError:
                printerror(f"Error: Permission denied to access '{path}'.")
                return
            files = []
            folders = []
            for item in raw:
                full_path = os.path.join(path, item)
                if os.path.isfile(full_path):
                    files.append(item)
                elif os.path.isdir(full_path):
                    folders.append(item)
            folders.sort()
            files.sort()
            for i in folders:
                print(f"{colorama.Fore.BLUE}{i}/ {colorama.Fore.RESET}")
            for i in files:
                print(f"{colorama.Fore.GREEN}{i} {colorama.Fore.RESET}")

    @api.command()
    class touch():
        def execute(args):
            if not os.path.exists(args[0]):
                open(args[0],"w")
                print("Created file",args[0])
                api.updatecompletions()
            else:
                printerror(f"Error: {args[0]} exists")

    @api.command(alias=["rm"])
    class remove():
        def execute(args):
            try:
                os.remove(os.path.join(api.starterdir,args[0]))
            except PermissionError:
                printerror(f"Error: Permission to delete '{args[0]}' denied")
            except FileNotFoundError:
                printerror(f"Error: '{args[0]}' does not exist.")

class mkdirCompleter(Completer):
        def __init__(self, api):
            self.api = api

        def get_completions(self, document, complete_event, api):
            self.api = api
            splitLine = document.current_line_before_cursor.split(" ")
            if len(splitLine) > 1:
                # try:
                    # try:
                    #     for i in os.listdir(os.path.join(self.api.pwd,splitLine[1])):
                    #         if i.startswith(splitLine[1]) or splitLine[1] == '':
                    #             yield Completion(i,start_position=document.current_line_before_cursor.find(splitLine[1])-document.cursor_position)
                    # except:
                    # try:
                        if len(splitLine[1].split("/"))  == 1:
                            self.offset = 0
                        else:
                            self.offset = 1
                        self.reconstrPath = ""
                        for i in splitLine[1].split("/")[0:len(splitLine[1].split("/"))-self.offset]:
                            self.reconstrPath = os.path.join(self.reconstrPath)
                        for i in os.listdir(os.path.join(os.getcwd(),self.reconstrPath)):
                            if splitLine[1].rfind("/") != -1:
                                if i.startswith(splitLine[1][splitLine[1].rfind("/")+1:len(splitLine[1])]) or splitLine[1][splitLine[1].rfind("/")+1:len(splitLine[1])] == '':
                                    yield Completion(i,start_position=splitLine[1].rfind("/")+4-document.cursor_position)
                            elif i.startswith(splitLine[1]):
                                yield Completion(i,start_position=document.current_line_before_cursor.find(splitLine[1])-document.cursor_position)
                    # except:
                    #     for i in os.listdir(self.api.pwd):
                    #         if i.startswith(splitLine[1]) or splitLine[1] == '':
                    #             yield Completion(i,start_position=document.current_line_before_cursor.find(splitLine[1])-document.cursor_position)