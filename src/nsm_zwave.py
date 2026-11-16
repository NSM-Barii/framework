# Z-WAVE PROTOCOL MODULE // NSM BARII
# Hardware layer -> nsm_hackrf.py
# Active attacks + S0 crypto -> nsm_z_shave.py


# REGULAR IMPORTS
import time, json, subprocess
import numpy as np
from pathlib import Path
from datetime import datetime
from rich.live import Live
from rich.panel import Panel


# NSM IMPORTS
from nsm_vars     import Variables
from nsm_hackrf   import Hack_RF
from nsm_database import FileSaving


# CONSTANTS
console    = Variables.console
ZWAVE_BAUD = 40e3
ZWAVE_DEV  = 20e3


# FILE SAVING
RECON_DIR = Path(__file__).resolve().parent.parent / "captures" / "zwave_recon"



CC_NAMES = {
    0x00: "NO_OP",        0x20: "BASIC",           0x25: "SWITCH_BINARY",
    0x26: "SWITCH_ML",    0x31: "SENSOR_ML",       0x40: "THERM_MODE",
    0x43: "THERM_SETPOINT", 0x44: "THERM_OP_STATE", 0x45: "THERM_FAN",
    0x62: "DOOR_LOCK",    0x71: "ALARM",           0x72: "MFG_SPECIFIC",
    0x80: "BATTERY",      0x84: "WAKE_UP",         0x86: "VERSION",
    0x98: "SECURITY_S0",  0x9F: "SECURITY_S2",
}

SEC_LEVEL = {0x98: "S0", 0x9F: "S2"}



FRAME_REF = {
    "home":    "a1b2c3d4",                 # bytes 0-3  — network ID (always plaintext)
    "src":     1,                           # byte 4     — sender (1 = controller)
    "dst":     5,                           # byte 8     — destination (5 = door lock)
    "fc":      (0x41, 0x01),                # bytes 5-6  — singlecast, seq=1
    "len":     12,                          # byte 7     — total frame length incl checksum
    "cc":      0x98,                        # byte 9     — SECURITY_S0
    "cmd":     0x40,                        # byte 10    — NONCE_GET
    "payload": "9840",                      # bytes 9 to len-2 as hex
    "raw":     "a1b2c3d40141010c0598406b",  # full frame incl checksum (0x6b)
    "ts":      "14:32:07",                  # timestamp when decoded
}






# ============================================================
#  DEMODULATOR
# ============================================================

class ZWave_Demod():
    """NRZ FSK demodulator for raw int8 IQ buffers"""


    @staticmethod
    def demod(buf: np.ndarray) -> list:
        if len(buf) < 200: return []

        iq   = buf[0::2] + 1j*buf[1::2]; iq -= iq.mean()
        iq   = np.convolve(iq, np.ones(13)/13, mode='same')
        inst = np.angle(iq[1:]*np.conj(iq[:-1]))*Variables.sample_rate/(2*np.pi)
        inst -= np.median(inst)
        inst  = np.convolve(inst, np.ones(5)/5, mode='same')
        sps   = int(Variables.sample_rate/ZWAVE_BAUD)
        c     = np.arange(sps//2, len(inst), sps).astype(int); c = c[c<len(inst)]
        bits  = (1-(inst[c]>0)).astype(np.int8)
        bs    = ''.join(map(str, bits))

        frames = []; search = 0
        while True:
            sof = bs.find('11110000', search+16)
            if sof < 0: break
            search = sof+1
            fb = bits[sof+8:]
            if len(fb) < 72: continue
            b  = fb[:len(fb)//8*8].reshape(-1,8)
            by = np.packbits(b, axis=1).flatten()
            if len(by) < 10: continue
            ln = int(by[7])
            if ln < 9 or ln > 64 or ln > len(by): continue
            chk = 0xFF
            for x in by[:ln-1]: chk ^= int(x)
            if chk != int(by[ln-1]): continue
            src = int(by[4]); dst = int(by[8])
            if not (1 <= src <= 232): continue
            if not (1 <= dst <= 232 or dst == 255): continue
            if by[0] in (0x00, 0xFF): continue
            payload = by[9:ln-1]
            cc = int(payload[0]) if len(payload) else None
            frames.append({
                "home"   : by[0:4].tobytes().hex(),
                "src"    : src,
                "dst"    : dst,
                "fc"     : (int(by[5]), int(by[6])),
                "len"    : ln,
                "cc"     : cc,
                "payload": payload.tobytes().hex() if len(payload) else "",
                "raw"    : by[:ln].tobytes().hex(),
                "ts"     : datetime.now().strftime("%H:%M:%S"),
            })
            
        return frames


    @staticmethod
    def demod_file(iq_file: str) -> list:
        """This method will be used to demod zwave traffic"""



        try:
            raw = np.fromfile(iq_file, dtype=np.int8).astype(np.float32)
            return ZWave_Demod.demod(raw)
        except Exception:
            return []





class ZWave_Recon():
    """Passive Z-Wave network recon — live streaming demod + network mapping"""


    z_homes = 0
    z_nodes = 0
    z_frames = 0

    @classmethod
    def _live(cls):
        """This method will be used to perform and show live ZWave traffic"""

        c1 = "bold yellow"

        cmd = [
            "hackrf_transfer", "-r", "-",
            "-f", str(int(Variables.modulation["zwave"])),
            "-s", str(int(Variables.sample_rate)),
            "-l", str(Variables.gain_lna),
            "-g", str(Variables.gain_vga),
            "-a", "1" if Variables.gain_amp else "0",
        ]

        network    = {}
        frame_count = 0
        chunk_size  = int(Variables.sample_rate * 0.5) * 2
        max_buf     = int(Variables.sample_rate * 2) * 2

        panel = Panel(renderable="Developed by NSM Barii", style="bold red", border_style="bold purple", expand=False)

        console.print(f"[bold yellow][*] Z-Wave live recon @ {Variables.modulation['zwave']/1e6:.3f} MHz — Ctrl+C to stop\n")

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        try:

            with Live(panel, console=console, refresh_per_second=4):

                buf = np.array([], dtype=np.float32)
                while True:
                    raw = proc.stdout.read(chunk_size)
                    if not raw: break

                    chunk = np.frombuffer(raw, dtype=np.int8).astype(np.float32)
                    buf   = np.concatenate([buf, chunk])
                    if len(buf) > max_buf: buf = buf[-max_buf:]

                    for f in ZWave_Demod.demod(buf):
                        cls._update_map(network, f)
                        if network[f["home"]]["frames"] < 2: continue
                        frame_count += 1
                        cls._print_frame(f, frame_count)

                    panel.renderable = f"Total Homes: [{c1}]{cls.z_homes}[/{c1}]  -  Total Nodes: [{c1}]{cls.z_nodes}[/{c1}]  -  Total Frames: [{c1}]{cls.z_frames}  -  [bold green]Developed by NSM Barii"


        except KeyboardInterrupt: pass
        finally: proc.terminate()

        confirmed = {h: d for h, d in network.items() if d["frames"] >= 2}
        console.print(f"\n[bold yellow][!] Stopped. {cls.z_frames} frames.\n")
        if confirmed:
            cls._print_map(confirmed)
            cls._save_map(confirmed)


    @staticmethod
    def _print_frame(f: dict, n: int):
        """This is soley responsible for printing valid ZWave frames"""

        cc_name = CC_NAMES.get(f["cc"], f"0x{f['cc']:02x}" if f["cc"] is not None else "?")
        sec     = f"[bold red]{SEC_LEVEL[f['cc']]}[/bold red]" if f["cc"] in SEC_LEVEL else "[dim]plain"

        console.print(
            f"[dim]{f['ts']}[/dim]  [bold cyan]#{n}[/bold cyan]  "
            f"[yellow]{f['home']}[/yellow]  {f['src']}→{f['dst']}  "
            f"{sec}  [green]{cc_name}[/green]  [dim]{f['payload'][:32]}[/dim]"
        )


    @classmethod
    def _update_map(cls, network: dict, f: dict):
        """This method will be used to update the map of a network"""


        home = f["home"]
        if home not in network:
            network[home] = {"nodes": {}, "frames": 0}

        network[home]["frames"] += 1

        for nid in (f["src"], f["dst"]):
            if nid not in network[home]["nodes"]:
                network[home]["nodes"][nid] = {"cc": set(), "sec": set(), "talks_to": set()}

        if f["cc"] is not None:
            network[home]["nodes"][f["src"]]["cc"].add(f["cc"])
            if f["cc"] in SEC_LEVEL:
                network[home]["nodes"][f["src"]]["sec"].add(SEC_LEVEL[f["cc"]])

        network[home]["nodes"][f["src"]]["talks_to"].add(f["dst"])

        confirmed = {h: d for h, d in network.items() if d["frames"] >= 2}
        cls.z_homes  = len(confirmed)
        cls.z_frames = sum(d["frames"] for d in confirmed.values())
        cls.z_nodes  = len({nid for d in confirmed.values() for nid in d["nodes"]})


    @staticmethod
    def _assess(data: dict) -> tuple:
        """This method will be used to assess whether the security used is S0, S2, or mixed"""

        all_cc = {c for n in data["nodes"].values() for c in n["cc"]}
        s0 = 0x98 in all_cc
        s2 = 0x9F in all_cc

        if s0 and not s2:   return "S0 ONLY - Z-SHAVE VULNERABLE", "bold red"
        elif s2 and not s0: return "S2 - SECURE", "bold green"
        elif s0 and s2:     return "MIXED S0+S2", "bold yellow"
        else:               return "PLAINTEXT", "bold red"


    # NOT 100% GURANTEED MATCHING (YET)
    @staticmethod
    def _guess_role(cc_set: set) -> str:
        """This method will be used to guess the role of the node"""

        if 0x62 in cc_set:                    return "Lock"
        if 0x40 in cc_set or 0x43 in cc_set:  return "Thermostat"
        if 0x25 in cc_set:                    return "Switch/Plug"
        if 0x31 in cc_set:                    return "Sensor"
        if 0x71 in cc_set:                    return "Alarm/Sensor"
        if 0x26 in cc_set:                    return "Dimmer"
        return "Unknown"


    @staticmethod
    def _print_map(network: dict):
        """This method will be used to print the network map"""

        console.print("\n[bold red]── Network Map ──[/bold red]\n")
        s0_nets, plain_nets = [], []

        for home, data in sorted(network.items(), key=lambda x: -x[1]["frames"]):
            tag, color = ZWave_Recon._assess(data)
            all_sec = {s for n in data["nodes"].values() for s in n["sec"]}

            if "S0" in all_sec:  s0_nets.append(home)
            elif not all_sec:    plain_nets.append(home)


        console.print(f"[bold red]Networks: [bold yellow]{len(network)}\n[bold red]S0 - Z-Shave Vulnerable: [bold yellow]{len(s0_nets)}")


    @staticmethod
    def _save_map(network: dict):
        """This method will be responsible for storing data within a json readable format"""


        if not network: return

        RECON_DIR.mkdir(parents=True, exist_ok=True)

        out = {
            home: {
                "frames": data["frames"],
                "nodes": {
                    str(nid): {
                        "role": "Controller" if nid == 1 else ZWave_Recon._guess_role(i["cc"]),
                        "cc": list(i["cc"]),
                        "sec": list(i["sec"]),
                        "talks_to": list(i["talks_to"]),
                    } for nid, i in data["nodes"].items()
                },
            } for home, data in network.items()
        }

        path = RECON_DIR / f"map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(path, "w") as f: json.dump(out, f, indent=2)
        console.print(f"[dim]Map saved: {path}[/dim]")


    @classmethod
    def main(cls):
        """This method will be used to control class wide code"""

        if not Variables.zwave_wardrive:  return False
        if not Variables.freq:            Variables.freq = Variables.modulation["zwave"]
        if not Hack_RF.present():         console.print("[bold red][-] hackrf_transfer not found"); return False


        cls._live()




class ZWave_Capture():
    """Z-Wave IQ capture + offline analysis"""


    @staticmethod
    def _record():



        duration = Variables.timeout
        offset   = Variables.freq_offset

        amp = Variables.gain_amp
        lna = Variables.gain_lna
        vga = Variables.gain_vga

        file_path = Variables.file_name
        

        center = Variables.modulation["zwave"] + offset

        c1 = "bold green"
        c2 = "bold yellow"
        c3 = "yellow"
        c4 = "bold red"



        panel = Panel(renderable="Developed by NSM Barii", style="bold red", border_style="bold purple", expand=False)



        stats = (
            f"\n\n[{c4}]=====  Constants ====="
            f"\n[{c1}]Freq:[{c2}] {Variables.freq} MHz (ZWave)",
            f"\n[{c1}]Center:[{c2}] {Variables.freq_offset} MHz",
            f"\n[{c1}]Duration:[{c2}] {Variables.timeout}",
            f"\n[{c1}]Gain:[{c2}] AMP: {True if Variables.gain_amp else False} | LNA: {Variables.gain_lna} | VGA: {Variables.gain_vga}",
            f"\n[{c1}]Out (file_path)[{c2}]: {Variables.file_name}"
            f"\n\n[{c4}]====================="
        )


        console.print(stats)


        with Live(panel, console=console, refresh_per_second=4):

            for n in range(3, 0, -1):
                
                panel.renderable = f"[bold red][!] Recording IQ in:[/bold red] {n}"
                time.sleep(1)

            panel.renderable = "[bold red][!] >>> RECORDING <<< [green]- Developed by NSM Barii"

            ok = Hack_RF.capture(freq=center, file_out=file_path, sample_rate=Variables.sample_rate, lna=lna, vga=vga, amp=amp, duration=duration)

            
        if not ok: return False

        console.print(f"\n\n[yellow][+] File_save path -->[/yellow] {Variables.file_name}")
        console.print(f"[bold green][+] ZWave capture successfully completed!")

        return file_path


    @staticmethod
    def _analyze():
        """This method will allow a user to pass an IQ file containing ZWave traffic to demodulate and display it"""


        console.print(f"\n\n[bold green][!] Attempting to demodulate:[yellow] {Variables.zwave_analyze}")
           

        try:

            frames   = ZWave_Demod.demod_file(iq_file=Variables.zwave_analyze)
            home_hex = Variables.zwave_home_hex
            
            if home_hex: frames = [f for f in frames if f["home"] == home_hex]

            if not frames: console.print("[bold red][-] No frames decoded nor found"); return []


            console.print(f"[bold green][+] {len(frames)} frame(s) decoded:\n")
            
            for i, f in enumerate(frames, 1):

                cc_name = CC_NAMES.get(f["cc"], f"0x{f['cc']:02x}" if f["cc"] else "?")
                sec     = SEC_LEVEL.get(f["cc"], "plain") if f["cc"] in SEC_LEVEL else "plain"


                console.print(
                    f"  [bold cyan]#{i}[/bold cyan]  [yellow]{f['home']}[/yellow]  "
                    f"{f['src']}→{f['dst']}  {sec}  [green]{cc_name}[/green]  "
                    f"[dim]{f['payload'][:40]}[/dim]"
                )
            return frames


        except Exception as e: console.print(f"[bold red][!] Exception Error:[yellow] {e}"); return False


    @classmethod
    def main(cls):
        """This method will be responsible for controlling class wide logic"""

        c1 = "yellow"
        c2 = "green"


        if not Variables.zwave_record and not Variables.zwave_analyze: return False
        if not Variables.freq: Variables.freq = (Variables.modulation["zwave"] + Variables.freq_offset / 1e6) * 1e6
        if not Hack_RF.present(): return False


        console.print(f"\n\n[{c2}]=====  Gain Settings  =====",
                      f"\nAMP: [{c1}]{Variables.gain_amp}\nLNA: [{c1}]{Variables.gain_lna}\nVGA: [{c1}]{Variables.gain_vga}[{c1}]"
        )
        if Variables.zwave_record: return cls._record()
        elif Variables.zwave_analyze: return cls._analyze()




if __name__ == "__main__":
    Variables.zwave_wardrive = True
    ZWave_Recon.main()
