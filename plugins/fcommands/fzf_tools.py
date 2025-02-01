import subprocess, sys
from typing import Callable

def fzf(command:str, work:Callable[[], None]) -> list[str]:
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, shell=True)
    original_stdout = sys.stdout
    sys.stdout = process.stdin
    try:
        work()
        process.stdin.close() # type: ignore
    except:
        pass
    finally:
        sys.stdout = original_stdout

    output = process.stdout.read().splitlines() # type: ignore
    process.stdout.close() # type: ignore
    return output

def work(options:list[str]) -> None:
    for option in options:
        print(option, flush=True)

def work_generator(options:list[str]) -> Callable[[], None]:
    return lambda: work(options=options)

def fzf_run(options:list[str], header:str|None=None, reverse:bool=False, multi:bool=False) -> list[str]:
    fzf_command = f"fzf{'' if header == None else ' --header "' + header + '"'}{' --reverse'}{' --multi'}"
    return fzf(command=fzf_command, work=work_generator(options=options))
