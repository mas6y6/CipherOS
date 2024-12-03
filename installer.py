import sys
import urllib.request, progressbar, os, colorama, requests, json, platform, subprocess

def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(widgets=["Downloading... ",progressbar.Percentage()," ",progressbar.Bar(left="[",right="]")," ",progressbar.AbsoluteETA()],maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None

def download(url):
    urllib.request.urlretrieve(
    url,
    os.path.join(os.path.expanduser("~"), ".cache","cipheros"),
    show_progress,
)


def run_with_sudo(command):
    try:
        full_command = ['sudo'] + command
        subprocess.run(full_command, check=True)
        print("Command executed successfully with admin privileges.")
    except subprocess.CalledProcessError:
        print("Admin privileges were denied or an error occurred.")

releases = requests.get("https://api.github.com/repos/mas6y6/CipherOS/releases/latest").json()

latest = releases["tag_name"]

system = platform.system()

print(
    colorama.Fore.LIGHTMAGENTA_EX
    + r"""   _______       __              ____  _____
  / ____(_)___  / /_  ___  _____/ __ \/ ___/
 / /   / / __ \/ __ \/ _ \/ ___/ / / /\__ \ 
/ /___/ / /_/ / / / /  __/ /  / /_/ /___/ / 
\____/_/ .___/_/ /_/\___/_/   \____//____/  
      /_/                                   

Project Codename: Paradox"""
    + colorama.Fore.RESET
)
print("\nCipherOS Installer for macOS and Linux")

if system == "Darwin":
    print("Finding CipherOS for macOS..")
    url = None
    for i in releases["assets"]:
        if i["name"] == "macos_raw-executable":
            url = i["url"]
            break
    if url == None:
        print(colorama.Fore.LIGHTRED_EX+"The executeable for macOS is not found.\nMaybe is still being developed on.\nContact @mas6y6 (on discord) if you need help"+colorama.Fore.RESET)
        sys.exit(1)
    else:
        print(f"Downloading {url}...")
        download(url)
        path1 = os.path.join(os.path.expanduser('~'), '.cache','cipheros')
        path2 = os.path.join("/usr","local","bin","cipheros")
        print("This script will require your admin password to continue because it will be be changeing the premissions for the executeable and moving the executeable to /usr/local/bin.\n")
        run_with_sudo("chmod +x "+path1)
        run_with_sudo("mv"+path1+path2)
        print("Installer completed!")
elif system == "Linux":
    print("Finding CipherOS for Linux..")
    url = None
    for i in releases["assets"]:
        if i["name"] == "linux_raw-executable":
            url = i["url"]
            break
    if url == None:
        print(colorama.Fore.LIGHTRED_EX+"The executeable for Linux is not found.\nMaybe is still being developed on.\nContact @mas6y6 (on discord) if you need help"+colorama.Fore.RESET)
        sys.exit(1)
    else:
        print(f"Downloading {url}...")
        download(url)
        path1 = os.path.join(os.path.expanduser('~'), '.cache','cipheros')
        path2 = os.path.join("/usr","local","bin","cipheros")
        print("This script will require your admin password to continue because it will be be changeing the premissions for the executeable and moving the executeable to /usr/local/bin.\n")
        run_with_sudo("chmod +x "+path1)
        run_with_sudo("mv"+path1+path2)
        print("Installer completed!")
elif system == "Windows":
    print(colorama.Fore.LIGHTRED_EX+"The CipherOS installer is not avaiable for Windows"+colorama.Fore.RESET)
    sys.exit(1)