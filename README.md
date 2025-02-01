# CipherOS

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mas6y6/CipherOS/refs/heads/main/logos/banner.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/mas6y6/CipherOS/refs/heads/main/logos/banner_black.png">
  <img alt="CipherOS logo" src="https://user-images.githubusercontent.com/25423296/163456779-a8556205-d0a5-45e2-ac17-42d089e3c3f8.png">
</picture>


An hacknet inspired hacking program

## How to install

### Windows
You can use the standalone .exe from [releases](https://github.com/mas6y6/CipherOS/releases), or you can clone the repository locally and use [pyinstaller](https://pyinstaller.org/en/stable/) with `compile.bat`

> [!NOTE]
> the standalone .exe will generate the `plugins` and `data` folder in the directory that the executable is run in, so it is recommended to drop the .exe in a dedicated folder before running.

### macOS / Linux
You can run this to download the installer
```sh
curl https://raw.githubusercontent.com/mas6y6/CipherOS/refs/heads/main/installer.sh -o installer.sh
```
To run the installer in sudo mode
```sh
sudo sh installer.sh
```
To use the automatic installer.

But if your architecture isn't supported you can build your own CipherOS build can just use the [compile.sh](https://github.com/mas6y6/CipherOS/blob/main/compile.sh) to compile the `main.py` file to `cipher`.

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
## Discord
[Click me](https://discord.gg/4HJrhKhWgj) to join the Cipher HackSquad discord server

# Contributors
+ [@mas6y6](https://github.com/mas6y6) (Owner)
+ [@malachi196](https://github.com/malachi196)
+ [@overo3](https://github.com/Overo3)

# Credits

None yet..
