from cipher.api import CipherAPI
from cipher.parsers import ConfigParser
from cipher.plugins import CipherPlugin
import shutil
from fcommands.fzf_tools import fzf_run
from prompt_toolkit import prompt

class FCommands(CipherPlugin):
    def __init__(self, api: CipherAPI, config:ConfigParser):
        super().__init__(api, config)
        self.help: dict[str, str] = {
            "fexe": "fexe allows the user to select a command using the \"fzf\"-tool.",
            "fhist": "Search command history using fzf and let's you execute the selected command."
        }
        
        self.__fzf_is_installed = shutil.which("fzf") != None
        self.register_commands()
    
    def on_enable(self):
        print("Example Plugin enabled")
    
    def register_commands(self) -> None:
        @self.command(desc=self.help["fexe"])
        def fexe(args:list[str]) -> None: # type: ignore
            if len(args) > 0:
                print(self.help["fexe"])
                return
            availible_commands = sorted([command for command in self.api.commands])
            descriptions: dict[str, str] = {
                command: (f" {(desc)}" if (desc:=self.api.commands[command].desc) != None else "") for command in availible_commands
            }
            longest_commands_length = max([len(command) for command in availible_commands])
            fzf_options = [
                f"{command}{" " * (longest_commands_length - len(command))}|{descriptions[command]}" for command in availible_commands
            ]
            fzf_output = fzf_run(options=fzf_options, header="Commands availible", multi=False)
            if fzf_output in [[], [""]]:
                print("No command selected.")
                return
            if len(fzf_output) > 1:
                raise IndexError(f"'fzf_output' should be of length 1 but is {len(fzf_options)}.")
            fzf_output_possible_commands = [command for command in availible_commands if fzf_output[0].startswith(command)]
            if len(fzf_output_possible_commands) == 0:
                raise IndexError(f"'fzf_output_possible_commands' should be of length 1 but is {len(fzf_output_possible_commands)}.")
            elif len(fzf_output_possible_commands) == 1:
                selected_command = fzf_output_possible_commands[0]
            else:
                selected_command = sorted(fzf_output_possible_commands, key=lambda x: len(x))[-1]
            try: selected_command_full = prompt(message=f"{self.api.commandlineinfo}> ", default=selected_command)
            except KeyboardInterrupt: return
            if selected_command_full == "": return
            self.api.run(f"{selected_command_full}".split(" "))
        
        @self.command(desc=self.help["fhist"])
        def fhist(args:list[str]) -> None: # type: ignore
            if len(args) > 0:
                print(self.help["fexe"])
                return
            leading_number_length = len(str(len(self.api.command_history)))
            fzf_options: list[str] = [f"{" " * (leading_number_length - len(f"{i}"))}{i}: {self.api.command_history[i]}"
                                      for i in range(len(self.api.command_history))]
            fzf_output = fzf_run(options=fzf_options, header="Commands executed", reverse=True, multi=False)
            if fzf_output in [[], [""]]:
                print("No command selected.")
                return
            if len(fzf_output) > 1:
                raise IndexError(f"'fzf_output' should be of length 1 but is {len(fzf_options)}.")
            selected_command = ": ".join(fzf_output[0].split(": ")[1:])
            try: selected_command_full = prompt(message=f"{self.api.commandlineinfo}> ", default=selected_command)
            except KeyboardInterrupt: return
            if selected_command_full == "": return
            print(f"runing\"{selected_command_full}\"")
            self.api.run(f"{selected_command_full}".split(" "))

