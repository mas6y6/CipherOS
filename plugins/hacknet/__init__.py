from cipher.plugins import CipherPlugin, CipherAPI
from rich.panel import Panel
import os, pygame, progressbar, time

class HacknetPlugin(CipherPlugin):
    def __init__(self, api: CipherAPI,config):
        super().__init__(api,config)
        self.register_commands()
        self.console = self.api.console
        self.traceactive = False
    
    def register_commands(self):
        """Method to register all commands for this plugin"""
        
        @CipherPlugin.command()
        def traced(args):
            if self.traceactive:
                self.console.bell()
                self.console.print(Panel("COMPLETED TRACE DETECTED ETAS PROTOCAL ALREADY ACTIVE\nCOMPLETE INTRUCTIONS NOW", expand=True,style="white on red"))
                self.console.print(Panel("""
EMERGENCY TRACE AVERSION SEQUENCE

Reset Assigned IP Address on ISP Mainframe
ISP Mainframe IP: (IP)
YOUR Assigned IP: (IP)
""", expand=True,style="white on red"))
                return
            else:
                if os.name == "nt":
                    os.system("color 40")
                elif os.name == "posix":
                    os.system("setterm -background red -foreground black -store")
                self.traceactive = True
            pygame.mixer.init()
            pygame.mixer.music.load(os.path.join(self.api.starterdir,"plugins","hacknet","dark_drone_008.ogg"))
            pygame.mixer.music.play(loops=-1)
            traced = pygame.mixer.Sound(os.path.join(self.api.starterdir,"plugins","hacknet","spiral_gauge_down.ogg"))
            traceddo = pygame.mixer.Sound(os.path.join(self.api.starterdir,"plugins","hacknet","spiral_gauge_up.ogg"))
            
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
                
                e.console.print("""\n Unsyndicated foreign connection detected during active trace
  :: Emergency recovery mode activated
 --------------------------------------------------------------

 Automated screening procedures will divert incoming connections temporarily
 This window is a final opportunity to regain anonymity.
 As your current IP Address is known, it must be changed -
 This can only be done on your currently active ISP's routing server
 Reverse tracerouting has located this ISP server's IP address as : (ISP address)
 Your local IP: (User address) must be tracked here and changed.

 Failure to complete this while active diversion holds will result in complete and permanent loss of all account data -
 THIS IS NOT REPEATABLE AND CANNOT BE DELAYED\n""",style="bold white on red")
                
                e.console.input("[bold white on red] Press Enter to BEGIN...[/]")
                traced.stop()
                traceddo.play()
                pygame.mixer.music.stop()
                pygame.mixer.music.load(os.path.join(self.api.starterdir,"plugins","hacknet","traced.ogg"))
                print("\033c", end="")
                print("\033[?25l")
                if os.name == "nt":
                    os.system("color 40")
                elif os.name == "posix":
                    os.system("setterm -background red -foreground black -store")
                e.console.print(Panel("INITIALIZING FAILSAFE", expand=True,style="white on red"))
                time.sleep(1.5)
                pygame.mixer.music.play()
                for i in range(5):
                    bar[i] = progressbar.ProgressBar(widgets=[" [",progressbar.Bar(),"]"])
                    bar[i].start()
                    print("")
                for z in range(100):
                    time.sleep(0.14)
                    for x in range(5):
                        bar[x].update(100-i)

                time.sleep(14)

            self.console.clear()
            self.console.print(Panel("""
EMERGENCY TRACE AVERSION SEQUENCE

Reset Assigned IP Address on ISP Mainframe
ISP Mainframe IP: (IP)
YOUR Assigned IP: (IP)
""", expand=True,style="white on red"))
            time.sleep(1)
        
        @CipherPlugin.command()
        def completetrace(args):
            if self.traceactive == False:
                self.console.bell()
                return
            
            with self.console.screen() as e:
                pygame.mixer.music.stop()
                completed = pygame.mixer.Sound(os.path.join(self.api.starterdir,"plugins","hacknet","spiral_gauge_down.ogg"))
                completed.play()
                beep = pygame.mixer.Sound(os.path.join(self.api.starterdir,"plugins","hacknet","beep.wav"))
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