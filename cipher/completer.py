from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion, WordCompleter, merge_completers
from commands import mkdirCompleter


class CipherCompleter(Completer):
    def __init__(self, api):
        self.api = api
    def get_completions(self, document, complete_event):
        if len(document.current_line_before_cursor.split(" ")) == 1:
            self.commandOptions = []
            # for i in self.api.commands:
            #     self.commandOptions.append(i["class"].__name__)
            self.commandOptions = WordCompleter(self.api.commands,ignore_case=True).get_completions(document, complete_event)
            for i in self.commandOptions:
                yield i

def get_full_completer(api):
    return merge_completers([CipherCompleter(api),mkdirCompleter(api)])

