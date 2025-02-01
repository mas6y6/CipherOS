import sys, platform, os, ctypes

def is_root() -> bool:
    system = platform.system()
    if system in ["Linux", "Darwin"]:
        try:
            return os.getuid() == 0
        except AttributeError:
            return False
    elif system == "Windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except AttributeError:
            return False
    else:
        raise NotImplementedError(f"Unsupported OS: {system}")

def elevate(show_console:bool=True, graphical:bool=True) -> None:
    """
    Re-launch the current process with root/admin privileges

    When run as root, this function does nothing.

    When not run as root, this function replaces the current process (Linux,
    macOS) or creates a child process, waits, and exits (Windows).

    :param show_console: (Windows only) if True, show a new console for the
        child process. Ignored on Linux / macOS.
    :param graphical: (Linux / macOS only) if True, attempt to use graphical
        programs (gksudo, etc). Ignored on Windows.
    """
    if sys.platform.startswith("win"):
        from elevate.windows import elevate
    else:
        from elevate.posix import elevate
    elevate(show_console, graphical)

