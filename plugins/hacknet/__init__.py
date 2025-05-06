import random
import shutil
import string
from cipher.api import CipherAPI
from cipher.parsers import ConfigParser, ArgumentParser
from cipher.plugins.plugins import CipherPlugin
from rich.panel import Panel
import os, pygame, time, subprocess, requests
from .cursor import hide, show

class HacknetPlugin(CipherPlugin):
    def __init__(self, api: CipherAPI, config:ConfigParser):
        super().__init__(api, config)
        self.register_commands()
        self.console = self.api.console
        self.traceactive = False
        self._ipAddress: str | None = None
        self._ispAddress: str | None = None
    
    @property
    def ipAddress(self) -> str:
        if self._ipAddress == None:
            self._ipAddress = requests.get("https://ifconfig.me/").text
        return self._ipAddress
    @ipAddress.setter
    def ipAddress(self, value:str) -> None:
        self._ipAddress = value
    @ipAddress.deleter
    def ipAddress(self) -> None:
        del self._ipAddress
    
    @property
    def ispAddress(self) -> str:
        if self._ispAddress == None:
            if os.name == "nt":
                tracert = subprocess.run(["tracert","-h","2","8.8.8.8"],capture_output=True).stdout
                self._ispAddress = tracert[int(tracert.rfind(b"["))+1:int(tracert.rfind(b"]"))].decode("UTF-8")
            elif os.name == "posix":
                tracert = subprocess.run(["traceroute","-m","2","8.8.8.8"],capture_output=True).stdout.decode(encoding="UTF-8", errors="replace").splitlines()[-1]
                self._ispAddress = tracert[int(tracert.rfind("("))+1:int(tracert.rfind(")"))]
        return self._ispAddress
    @ispAddress.setter
    def ispAddress(self, value:str) -> None:
        self._ispAddress = value
    @ispAddress.deleter
    def ispAddress(self) -> None:
        del self._ispAddress
    
    def register_commands(self):
        """Method to register all commands for this plugin"""
        
        @self.command(desc="EMERGENCY TRACE AVERSION SEQUENCE")
        def traced(argsraw:list[str]):
            parser = ArgumentParser(self.api,"EMERGENCY TRACE AVERSION SEQUENCE")
            parser.parse_args(argsraw)
            
            if parser.help_flag:
                return None
            
            if self.traceactive:
                self.console.bell()
                self.console.print(Panel("COMPLETED TRACE DETECTED ETAS PROTOCAL ALREADY ACTIVE\nCOMPLETE INTRUCTIONS NOW", expand=True,style="white on red"))
                self.console.print(Panel(f"""
EMERGENCY TRACE AVERSION SEQUENCE

Reset Assigned IP Address on ISP Mainframe
ISP Mainframe IP: {self.ispAddress}
YOUR Assigned IP: {self.ipAddress}
""", expand=True,style="white on red"))
                return
            else:
                if os.name == "nt":
                    os.system("color 40")
                elif os.name == "posix":
                    if 'darwin' in os.uname().sysname.lower():
                        os.system("tput setab 1")
                    else:
                        os.system("setterm -background red -foreground black -store")
                self.traceactive = True
            pygame.mixer.init()
            pygame.mixer.music.load(os.path.join(self.api.configdir,"plugins","hacknet","dark_drone_008.ogg"))
            pygame.mixer.music.play(loops=-1)
            traced = pygame.mixer.Sound(os.path.join(self.api.configdir,"plugins","hacknet","spiral_gauge_down.ogg"))
            traceddo = pygame.mixer.Sound(os.path.join(self.api.configdir,"plugins","hacknet","spiral_gauge_up.ogg"))
            
            traced.play()
            with self.console.screen(style="on bright_red") as e:
#                 e.console.print(Panel(r""" _       _____    ____  _   _______   ________
# | |     / /   |  / __ \/ | / /  _/ | / / ____/
# | | /| / / /| | / /_/ /  |/ // //  |/ / / __  
# | |/ |/ / ___ |/ _, _/ /|  // // /|  / /_/ /  
# |__/|__/_/  |_/_/ |_/_/ |_/___/_/ |_/\____/   
#                                             """, expand=True,style="black on red"))
                e.console.print(Panel(r"""██     ██  █████  ██████  ███    ██ ██ ███    ██  ██████  
██     ██ ██   ██ ██   ██ ████   ██ ██ ████   ██ ██       
██  █  ██ ███████ ██████  ██ ██  ██ ██ ██ ██  ██ ██   ███ 
██ ███ ██ ██   ██ ██   ██ ██  ██ ██ ██ ██  ██ ██ ██    ██ 
 ███ ███  ██   ██ ██   ██ ██   ████ ██ ██   ████  ██████  """,expand=True,style="black on red"))
                e.console.print(Panel("COMPLETE TRACE DETECTED : EMERGENCY RECOVERY MODE ACTIVE", expand=True,style="black on red"))
                
                e.console.print(f"""\n Unsyndicated foreign connection detected during active trace
  :: Emergency recovery mode activated
 --------------------------------------------------------------

 Automated screening procedures will divert incoming connections temporarily
 This window is a final opportunity to regain anonymity.
 As your current IP Address is known, it must be changed -
 This can only be done on your currently active ISP's routing server
 Reverse tracerouting has located this ISP server's IP address as : {self.ispAddress}
 Your local IP: {self.ipAddress} must be tracked here and changed.

 Failure to complete this while active diversion holds will result in complete and permanent loss of all account data -
 THIS IS NOT REPEATABLE AND CANNOT BE DELAYED\n""",style="bold white on red")
                
                e.console.input("[bold white on red] Press Enter to BEGIN...[/]")
                traced.stop()
                traceddo.play()
                pygame.mixer.music.stop()
                pygame.mixer.music.load(os.path.join(self.api.configdir,"plugins","hacknet","Traced.ogg"))
                print("\033c", end="")
                hide()
                if os.name == "nt":
                    os.system("color 40")
                elif os.name == "posix":
                    if 'darwin' in os.uname().sysname.lower():
                        os.system("tput setab 1")
                    else:
                        os.system("setterm -background red -foreground black -store")
                e.console.print(Panel("INITIALIZING FAILSAFE", expand=True,style="white on red"))
                time.sleep(1.5)
                pygame.mixer.music.play()
                '''
                bar = {}
                for i in range(5):
                    bar[i] = progressbar.ProgressBar(widgets=[" [",progressbar.Bar(),"]"])
                    bar[i].start()
                    print("")
                for z in range(100):
                    time.sleep(0.14)
                    for x in range(5):
                        bar[x].update(100-z)
                '''
                columns, _ = shutil.get_terminal_size()
                for _ in range(110):
                    hide()
                    time.sleep(0.13)
                    random_string = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=columns))
                    self.console.print(str(random_string),style="white on red",markup=False,highlight=False)

                #time.sleep(14)
                show()
            self.console.clear()
            self.console.print(Panel(f"""
EMERGENCY TRACE AVERSION SEQUENCE

Reset Assigned IP Address on ISP Mainframe
ISP Mainframe IP: {self.ispAddress}
YOUR Assigned IP: {self.ipAddress}
""", expand=True,style="white on red"))
            time.sleep(1)
        
        @self.command(desc="Stops the EMERGENCY TRACE AVERSION SEQUENCE")
        def completetrace(argsraw:list[str]):
            parser = ArgumentParser(self.api,"Stops the EMERGENCY TRACE AVERSION SEQUENCE")
            parser.parse_args(argsraw)
            
            if parser.help_flag:
                return None
            
            if self.traceactive == False:
                self.console.bell()
                return
            
            with self.console.screen() as e:
                pygame.mixer.music.stop()
                completed = pygame.mixer.Sound(os.path.join(self.api.configdir,"plugins","hacknet","spiral_gauge_down.ogg"))
                completed.play()
                beep = pygame.mixer.Sound(os.path.join(self.api.configdir,"plugins","hacknet","beep.wav"))
                e.console.print(Panel("""

DISCONNECTED

""", expand=True,style="bold grey50"))
                self.traceactive = False
                time.sleep(3)
                e.console.print("IP Address successfully reset.....")
                time.sleep(3)
                e.console.print("Foreign trace averted.....")
                time.sleep(3)
                e.console.print("Preparing for system reboot.....")
                time.sleep(1)
            self.console.clear()
            time.sleep(20)
            self.console.print(Panel("Reboot Successful", expand=True,style="bold grey50"))
            beep.play()
            time.sleep(0.05)
            beep.play()
            pygame.mixer.quit()