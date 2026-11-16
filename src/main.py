# THIS MODULE WILL BE THE MAIN PILLAR IN THE BLE HACKING FRAMEWORK



# UI IMPORTS
from ast import arg
from numpy import var
from rich.panel import Panel
import pyfiglet


# ETC IMPORTS
import argparse, sys


# NSM MODULES
from nsm_vars import Variables
from nsm_ble import BLE_Enumerater, BLE_Sniffer, BLE_Fuzzer, BLE_Connection_Spam
from nsm_wifi import SSID_Sniffer, Client_Sniffer, Deauth_Attacker, Evil_Twin, Beacon_Flooder, War_Driving, You_Cant_DOS_ME
from nsm_telnet import Telnet_Brute_Forcer
from nsm_database import DataBase
from nsm_flock import Flock_Spoofer
from nsm_zwave import ZWave_Capture, ZWave_Recon
from nsm_hackrf import Hack_RF
from nsm_arp import ARP_Controller
from nsm_ssdp_mdns import LAN_Sniffer

# CONSTANTS
console = Variables.console




class Main_Menu():
    """This class will gatekeep program wide logic"""


    @staticmethod
    def main():
        """Main entry point"""

        data = (
            "\n       [bold cyan]IoT Exploitation Framework[/bold cyan]"
            "\n\n            [bold yellow]BLE • WiFi • UART[/bold yellow]"
            "\n\n              [bold magenta]Made by NSM-Barii[/bold magenta]\n"
        )

        panel = Panel(renderable=data, expand=False, style="bold red")


        parser = argparse.ArgumentParser(
            description="IOT Framework for Wireless Recon, Fuzzing & Hacking",
            add_help=False
        )

        parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")


        # ============
        #     BLE
        # ============
        parser.add_argument("-bw", action="store_true", help="BLE wardriving with automatic data logging")
        parser.add_argument("-bwv", action="store_true", help="BLE wardriving with verbose output")

        parser.add_argument("-bs", action="store_true", help="BLE scan")
        parser.add_argument("-bsv", action="store_true", help="BLE scan with vendor lookup")

        parser.add_argument("-bd", action="store_true", help="BLE dump GATT services from target (-m required)")

        parser.add_argument("-bc", action="store_true", help="BLE connection spam attack (-m required)")
        parser.add_argument("-bcp", action="store_true", help="BLE connection + pairing spam attack (-m required)")

        parser.add_argument("-bf", action="store_true", help="BLE fuzz all characteristics (-m required)")
        parser.add_argument("-bft", help="BLE fuzz specific characteristic UUID (-m required)")
        parser.add_argument("--send", help="Write properties: write, read, notify, all (default: write)")
        parser.add_argument("--response", help="Write-response flag: 0 or 1")
        parser.add_argument("--type", help="Fuzzing type (default: 1)")


        # ============
        #    WiFi
        # ============
        parser.add_argument("-ws", action="store_true", help="WiFi SSID scan")
        parser.add_argument("-wc", help="WiFi client scan from specific SSID (provide BSSID/MAC)")
        parser.add_argument("-wd", help="WiFi deauth attack on SSID (provide BSSID/MAC)")
        parser.add_argument("-wb", help="WiFi beacon flood (provide portal choice 1-3)")
        parser.add_argument("-we", help="WiFi evil twin attack (provide portal number 1-20)")
        parser.add_argument("-ww", action="store_true", help="WiFi wardriving mode")
        parser.add_argument("-wp", action="store_true", help="Use this to test pinging of yourself to see if your online, meant to be defensive against offensive methods")
        parser.add_argument("-fs", action="store_true", help="Spoof Flock camera probe requests (-i required)")

        parser.add_argument("-mm", help="Change iface to monitor mode")

        parser.add_argument("--channel", type=int, help="WiFi channel (default: 6)")
        parser.add_argument("--hop-delay", type=float, help="delay between hopping channels")
        parser.add_argument("--mode", type=int, help="Wardrive mode: 1=APs only, 2=clients+non-beacon (default: 1)")
        parser.add_argument("--src", help="Deauth source")
        parser.add_argument("--dst", help="Deauth destination MAC (default: ff:ff:ff:ff:ff:ff)")
        parser.add_argument("--inter", type=float, help="Packet send interval")
        parser.add_argument("--loop", type=int, help="Packet send loop count")
        parser.add_argument("--count", type=int, help="Number of packets to send")
        parser.add_argument("--realtime", action="store_true", help="Enable realtime packet sending")
        parser.add_argument("--reasons", help="Deauth reason codes (comma-separated, default: 4,5,7,15)")


        # ==========================
        #   GENERIC // ALL MODULES
        # ==========================
        parser.add_argument("-t", type=float, default=10, help="Scan timeout / delay in seconds (default: 10)")
        parser.add_argument("-m", help="Target MAC address")
        parser.add_argument("-i", "--iface", help="Network interface (default: wlan1)")       
        parser.add_argument("--delay", help="This option will be used to set a delay in between repeated operations!")
        parser.add_argument("--subnet", help="This option will be used to pass along subnet/cidr") 
        parser.add_argument("--router-ip", help="This option will be used to spoof the routers IP")
        parser.add_argument("--router-mac", help="This option will be used to spoof the routers MAC, if not given program will send an ARP request to the routers ip asking for its mac")
        parser.add_argument("--fake-mac", default="00:12:ff:12:44:12", help="This option will be used to pass along a fake mac address that will be used for poisoning/spoofing")


        # ===============
        #  Telnet
        # ===============
        parser.add_argument("--telnet", action="store_true", help="Telnet dictionary attack")



        # ============
        # mDNS/SSDP
        # ============
        parser.add_argument("-discover", action="store_true", help="This option will allow for LAN device discovery via both mDNS and SSDP")



        # ======
        # ARP
        # ======
        parser.add_argument("-arp-scan", action="store_true", help="This option will allow for an arp scan")
        parser.add_argument(f"-arp-poison", action="store_true", help="This option will allow use to perform an ARP Poison attack. Commands needed: -m (will default to spamming all devices if not given one), -i (will use default if not given one), --subnet, --fake-mac (will use default if not given one), --router-ip")

        # ===========
        #  ZWave
        # ===========
        parser.add_argument("-zr", action="store_true", help="This option will be used to record a zwave traffic on 908.40 MHz")
        parser.add_argument("-zw", action="store_true", help="This option will be used to view live ZWave traffic on 908.40MHz")
        parser.add_argument("-za", help="This option will be used to pass a IQ file containing ZWave traffic to later be demodulated and analyze")
        parser.add_argument("--home-hex", help="This option will allow a user to pass the home hex of which we will use as a filter when parsing through given IQ file")
    
       



        # ============
        # Generic SDR
        # ============
        parser.add_argument("--capture", action="store_true", help="This option will be used to capture zwave traffic")
        parser.add_argument("--freq", type=float, help="This option will be used to control center frequency")

        parser.add_argument("--amp", default=14, type=int, help="This option will be used to control amp")
        parser.add_argument("--lna", default=24, type=int, help="This option will be used to control lna")
        parser.add_argument("--vga", default=24, type=int, help="This option will be used to control vga")

        parser.add_argument("--sample-rate", default=2e6, type=float, help="This will be used to control sample rate")

        parser.add_argument("--save", action="store_true", help="This option will be used to save a file")
        parser.add_argument("--x", help="This option will be used to give a custom name to the capture")





        args = parser.parse_args()



        if args.help or len(sys.argv) == 1:
            console.print(panel)
            parser.print_help()
            exit()

        

        # SDR GENERIC
        Variables.freq    = args.freq
        Variables.sample_rate = args.sample_rate

        Variables.gain_amp = args.amp
        Variables.gain_lna = args.lna
        Variables.gain_vga = args.vga

        Variables.gain_capture = args.capture

        
        # GENERIC CONFIG
        Variables.timeout   = args.t
        Variables.delay     = args.delay or 2
        Variables.mac       = args.m
        Variables.iface     = args.iface or "wlan1"
        Variables.channel   = args.channel or 6
        Variables.hop_delay = args.hop_delay or 0.25
        Variables.mode      = args.mode or 1        
        Variables.inter     = args.inter or 0
        Variables.loop      = args.loop  or 0
        Variables.count     = args.count or 1
        Variables.realtime  = args.realtime

        Variables.file_save = True if args.save else False
        Variables.file_name = args.x

 
        # DEAUTH ATTACK
        Variables.mac_dst   = args.dst or "ff:ff:ff:ff:ff:ff"
        Variables.mac_src   = args.src or False


        if args.reasons:  Variables.reasons = [int(r.strip()) for r in args.reasons.split(',')]
        else:             Variables.reasons = [4, 5, 7, 15] 

        # BLE
        Variables.ble_wardrive        = args.bw or args.bwv
        Variables.war                 = args.bw
        Variables.ble_sniffer         = args.bs or args.bsv
        Variables.scan                = args.bs
        Variables.vendor              = args.bwv or args.bsv
        Variables.ble_enumeration     = args.bd

        if args.bf or args.bft:
            Variables.ble_fuzzer  = True
            Variables.fuzz        = args.bf
            Variables.fuzz_u      = args.bft or False
            Variables.send        = args.send or "write"
            Variables.response    = args.response or False
            Variables.f_type      = args.type or 1

        if args.bc or args.bcp:
            Variables.ble_connection_spam = True
            Variables.conn                = args.bc
            Variables.pair                = args.bcp or False

        # WiFi
        Variables.wifi_ssid_sniffer   = args.ws
        Variables.wifi_client_sniffer = bool(args.wc);  Variables.mac_client = args.wc
        Variables.wifi_deauth_attack  = bool(args.wd);  Variables.mac_src    = args.wd or False
        Variables.wifi_beacon_flood   = bool(args.wb);  Variables.portal_num = args.wb
        Variables.wifi_evil_twin      = bool(args.we);  Variables.portal_num = args.we
        Variables.wifi_wardrive       = args.ww
        Variables.wifi_ping_me        = args.wp
        Variables.flock_spoof         = args.fs

        # Network
        Variables.telnet              = args.telnet
        Variables.ip_subnet           = args.subnet   
        Variables.ip_router           = args.router_ip
        Variables.mac_router          = args.router_mac
        Variables.mac_fake            = args.fake_mac 
        
        # ZWave
        Variables.zwave_wardrive = args.zw
        Variables.zwave_record   = args.zr
        Variables.zwave_analyze  = args.za

        Variables.zwave_home_hex = args.home_hex


        # ARP
        Variables.arp_scan   = args.arp_scan
        Variables.arp_poison = args.arp_poison


        # mDNS/SSDP
        Variables.discover = args.discover




        if args.mm: DataBase.WiFi.monitor_mode(iface=args.mm)



        text = pyfiglet.figlet_format(text="Framework")
        console.print(f"[bold red]{text}")

        console.print(
            "\n       [bold cyan]IoT Exploitation & Wireless Research[/bold cyan]"
            "\n\n         [bold yellow]BLE • WiFi • Z-Wave • Sub-GHz • SDR[/bold yellow]"
            "\n\n              [bold magenta]Made by NSM-Barii[/bold magenta]\n"
        )
        print("\n")



        BLE_Sniffer.main();  BLE_Enumerater.main(); BLE_Fuzzer.main(); BLE_Connection_Spam.main()
        SSID_Sniffer.main(); Client_Sniffer.main(); Deauth_Attacker.main(); Beacon_Flooder.main(); Evil_Twin.main(); War_Driving.main(); You_Cant_DOS_ME.main()

        Flock_Spoofer.main()

        Telnet_Brute_Forcer.main()

        Hack_RF.main()

        ZWave_Recon.main(); ZWave_Capture.main()

        ARP_Controller.main()

        LAN_Sniffer.main()



if __name__ == "__main__": Main_Menu.main()
