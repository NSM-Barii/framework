# THIS MODULE WILL HOUSE ALL HACKRF HARDWARE INTERACTION // NSM BARII


# REGULAR IMPORTS
import shutil, subprocess, os
import numpy as np
from pathlib import Path


# NSM IMPORTS
from nsm_vars import Variables
from nsm_database import FileSaving


# CONSTANTS
console = Variables.console




class Hack_RF():
    """Pure HackRF hardware layer: detect, capture RX, FSK modulate, transmit TX"""


    @classmethod
    def present(cls):
        """Check if hackrf_info is installed and a device is connected"""


        if shutil.which("hackrf_info") is None:
            console.print("[bold red][-] hackrf_info not found![yellow] Install hackrf tools first!")
            return False

        out = subprocess.run(["hackrf_info"], capture_output=True, text=True)

        if "No HackRF boards found" in out.stdout + out.stderr:
            console.print("[bold red][-] HackRF not detected!")
            return False

        return True



    @classmethod
    def capture(cls, freq, file_out, sample_rate=None, lna=None, vga=None, amp=None, duration=None):
        """This method will be used to capture raw IQ Signals"""


        sample_rate = sample_rate or Variables.sample_rate
        lna         = lna         or Variables.gain_lna
        vga         = vga         or Variables.gain_vga
        amp         = amp         if amp is not None else Variables.gain_amp
        duration    = duration    or Variables.timeout

        n_bytes = int(sample_rate * 2 * duration)

        cmd = [
            "hackrf_transfer",
            "-n", str(n_bytes),
            "-r", str(file_out),
            "-f", str(int(freq)),
            "-s", str(int(sample_rate)),
            "-l", str(lna),
            "-g", str(vga),
            "-a", "1" if amp else "0",
        ]

        console.print(f"[bold yellow][*] Capturing {duration}s @ {int(freq)/1e6:.3f} MHz -> {file_out}")

        try:
            result = subprocess.run(cmd)
        except subprocess.TimeoutExpired:
            console.print("[bold red][-] hackrf_transfer timed out")
            return False

        if result.returncode != 0:
            console.print(f"[bold red][-] hackrf_transfer failed (rc={result.returncode})")
            return False

        console.print(f"[bold green][+] Capture complete[yellow] --> [bold green]{file_out}")
        return True


    @staticmethod
    def modulate_fsk(frame_bytes: bytes, sample_rate: float = 2e6,
                     baud: float = 40e3, deviation: float = 20e3,
                     preamble_len: int = 10) -> np.ndarray:
        """FSK modulate raw frame bytes -> int8 I/Q samples for hackrf_transfer -t

        Z-Wave R2: 40 kbps NRZ, ±20 kHz deviation, MSB-first bit order.
        On-air layout: preamble (N x 0x55) | SOF (0xF0) | frame_bytes
        Output: int8 I/Q interleaved pairs (hackrf_transfer native format)
        """


        # build on-air byte sequence
        preamble  = bytes([0x55] * preamble_len)
        sof       = bytes([0xF0])
        raw_bytes = np.frombuffer(preamble + sof + frame_bytes, dtype=np.uint8)

        # unpack to bits, MSB first
        bits = np.unpackbits(raw_bytes)

        # samples per bit
        sps = int(sample_rate / baud)           # 50 @ 2 Msps / 40 kbps

        # instantaneous frequency: bit=1 -> +deviation, bit=0 -> -deviation
        freq_seq = np.repeat(
            np.where(bits == 1, deviation, -deviation).astype(np.float64),
            sps
        )

        # continuous phase FSK: integrate freq to get phase
        phase = np.cumsum(2.0 * np.pi * freq_seq / sample_rate)

        # complex IQ baseband signal
        iq = np.exp(1j * phase)

        # scale to int8 with headroom
        scale   = 100
        i_int8  = (np.real(iq) * scale).astype(np.int8)
        q_int8  = (np.imag(iq) * scale).astype(np.int8)

        # interleave I, Q
        out        = np.empty(len(i_int8) * 2, dtype=np.int8)
        out[0::2]  = i_int8
        out[1::2]  = q_int8

        return out


    @classmethod
    def transmit(cls, freq, file_in, sample_rate=None, vga=None, amp=None):
        """Transmit raw IQ file via hackrf_transfer -t (one shot, no repeat)"""

        sample_rate = sample_rate or Variables.sample_rate
        vga         = vga         or Variables.gain_vga
        amp         = amp         if amp is not None else Variables.gain_amp

        cmd = [
            "hackrf_transfer",
            "-t", str(file_in),
            "-f", str(int(freq)),
            "-s", str(int(sample_rate)),
            "-x", str(vga),
            "-a", "1" if amp else "0",
        ]

        console.print(f"[bold yellow][*] TX {Path(file_in).name} @ {int(freq)/1e6:.3f} MHz")

        result = subprocess.run(cmd, capture_output=True)

        if result.returncode != 0:
            console.print(f"[bold red][-] TX failed (rc={result.returncode})")
            return False

        return True


    @classmethod
    def transmit_frame(cls, freq, frame_bytes: bytes, iq_path: str,
                       sample_rate: float = 2e6, baud: float = 40e3,
                       deviation: float = 20e3):
        """Modulate frame_bytes to FSK IQ, save to iq_path, transmit"""

        iq = cls.modulate_fsk(frame_bytes, sample_rate=sample_rate,
                               baud=baud, deviation=deviation)
        iq.tofile(iq_path)

        return cls.transmit(freq, iq_path, sample_rate=sample_rate)


    @classmethod
    def main(cls):
        """This will gatekeep using the hackrf from main"""


        if not Variables.gain_capture: return False

        if Variables.zwave_record: Variables.freq = Variables.modulation["zwave"]

        if not Variables.freq: console.print("[bold red][!] no freq given goofy!"); return False


        FileSaving.make_file_name()


        if Variables.gain_capture: cls.capture(freq=Variables.freq, file_out=Variables.file_save)