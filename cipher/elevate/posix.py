import errno
import os
import sys
from shlex import quote

def quote_shell(args:list[str]) -> str:
    return " ".join(quote(arg) for arg in args)


def quote_applescript(string:str) -> str:
    charmap = {
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
        "\"": "\\\"",
        "\\": "\\\\",
    }
    return '"%s"' % "".join(charmap.get(char, char) for char in string)


def elevate(show_console:bool=True, graphical:bool=True) -> None:
    if os.getuid() == 0:
        return

    args = [sys.executable] + sys.argv
    commands: list[list[str]] = []

    if graphical:
        if sys.platform.startswith("darwin"):
            commands.append([
                "osascript",
                "-e",
                "do shell script %s "
                "with administrator privileges "
                "without altering line endings"
                % quote_applescript(quote_shell(args))])

        if sys.platform.startswith("linux") and os.environ.get("DISPLAY"):
            commands.append(["pkexec"] + args)
            commands.append(["gksudo"] + args)
            commands.append(["kdesudo"] + args)

    commands.append(["sudo"] + args)

    for args in commands:
        try:
            os.execlp(args[0], *args)
        except OSError as e:
            if e.errno != errno.ENOENT or args[0] == "sudo":
                raise
