# CipherOS

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="logos/banner.png">
  <source media="(prefers-color-scheme: light)" srcset="logos/banner_black.png">
  <img alt="CipherOS logo" src="https://user-images.githubusercontent.com/25423296/163456779-a8556205-d0a5-45e2-ac17-42d089e3c3f8.png">
</picture>


An hacknet inspired hacking program

## Contents
- [Features](#features)
- [How to install](#how-to-install)
- [Running from source](#running-from-source)
- [About](#about)

## Features
- modular plugin system (see [plugins.md](plugins.md))
- probably more stuff

## How to install

### Windows
You can use the standalone .exe from [releases](https://github.com/mas6y6/CipherOS/releases), or you can clone the repository locally and use [pyinstaller](https://pyinstaller.org/en/stable/) with `compile.bat`

> [!NOTE]
> the standalone .exe will generate the `plugins` and `data` folder in the directory that the executable is run in, so it is recommended to drop the .exe in a dedicated folder before running.

### macOS / Linux
You can install this project using one of the three commands below.\
Install using `curl`
```shell
sh -c "$(curl -fsSL https://raw.githubusercontent.com/mas6y6/CipherOS/refs/heads/main/installer.sh)"
```
Install using `wget`
```shell
sh -c "$(wget -O- https://raw.githubusercontent.com/mas6y6/CipherOS/refs/heads/main/installer.sh)"
```
Install using `fetch`
```shell
sh -c "$(fetch -o - https://raw.githubusercontent.com/mas6y6/CipherOS/refs/heads/main/installer.sh)"
```

But if your architecture isn't supported you can build your own CipherOS build can just use the [compile.sh](compile.sh) to compile the `main.py` file to `cipher` or [run CipherOS from source](#running-from-source).

And download the cipher folder and put it in the same directory as `cipher`
```tree
.
├── cipher
│   ├── plugins.py
│   ├── argumentparser.py
│   ├── icon.ico
│   ├── api.py
│   ├── network.py
│   └── exceptions.py
└── cipher (This is an executeable)
```
> [!IMPORTANT]
> **The `cipher` folder must be in the SAME folder as the executeable!**

## Running from source
### getting the code
Download the project either [here](https://github.com/mas6y6/CipherOS/archive/refs/heads/main.zip) or using
```shell
git clone https://github.com/mas6y6/CipherOS.git
```
### getting the requirements
Note: I (tex) can only provide detailed information for linux. If you use a different operating system and are having trouble, google will be your friend. On websites like stackexchange there are usually answers for your problems.\

Install python (for example from [python.org](python.org)). The minimum version required is `3.12`.\
\
Navigate a terminal to the downloaded project's folder.
<details>
<summary>Optional: using a virtual environment</summary>

I recommend to use a [virtual environment](https://docs.python.org/3/library/venv.html) for installing the required packages. To do this, run
```shell
python3 -m pip install venv
python3 -m venv venv
source venv/bin/activate
```
If you do this, you'll have to run `source venv/bin/activate` every time you want to run the program, but you are not risking to break any system-required libraries or requirements for other projects.
</details>

Now install the requirements of this project using the command
```shell
pip install -r requirements.txt
```
And finally, to run the program, run
```shell
python3 main.py
```

## About
[Click me](https://discord.gg/4HJrhKhWgj) to join the Cipher HackSquad discord server

### Contributors
+ [@mas6y6](https://github.com/mas6y6) (original author)
+ [@malachi196](https://github.com/malachi196)
+ [@overo3](https://github.com/Overo3)
+ [@tex479](https://github.com/TEX479)

### Credits
None yet..
