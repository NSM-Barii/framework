# IoT Exploitation Framework

A wireless security research toolkit for vulnerability discovery and CVE hunting across BLE, WiFi, and Sub-GHz (Z-Wave, 433 MHz) attack surfaces. Built around HackRF One and RTL-SDR for RF capture, demodulation, and transmission.

> **This project is actively in development.** Sub-GHz modules are expanding — Z-Wave is the primary research target, with 433 MHz OOK, LoRa, and additional sub-GHz protocols planned. RTL-SDR support for passive receive-only operations is coming alongside HackRF for full TX/RX.

This framework centralizes and builds on code from my standalone tools:
[Bluehound](https://github.com/NSM-Barii/bluehound) (BLE),
[Netcracker](https://github.com/NSM-Barii/netcracker) (WiFi),
[Flock-back](https://github.com/NSM-Barii/flock-back) (Flock ALPR detection),
[Ezra](https://github.com/NSM-Barii/Ezra) (mDNS/SSDP discovery),
and [Netalert-2.0](https://github.com/NSM-Barii/netalert-2.0) (ARP).

---

## Modules

### Sub-GHz / SDR

| Module | File | Status |
|---|---|---|
| **HackRF Hardware Layer** | `nsm_hackrf.py` | Working — capture, FSK modulate, transmit |
| **Z-Wave Passive Recon** | `nsm_zwave.py` | Working — live demod, network mapping, IQ capture + analysis |
**Z-Wave capabilities:**
- Live 908.42 MHz FSK demodulation with real-time frame decoding
- Automatic network mapping — nodes, command classes, security level detection (S0/S2/plaintext)

### BLE

| Module | File | Status |
|---|---|---|
| **BLE Sniffer / Wardriver** | `nsm_ble.py` | Working |
| **BLE GATT Enumerator** | `nsm_ble.py` | Working |
| **BLE Fuzzer** | `nsm_ble.py` | Working |
| **BLE Connection Spam** | `nsm_ble.py` | Working |

### WiFi

| Module | File | Status |
|---|---|---|
| **SSID Scanner** | `nsm_wifi.py` | Working |
| **Client Sniffer** | `nsm_wifi.py` | Working |
| **Deauth Attack** | `nsm_wifi.py` | Working |
| **Beacon Flood** | `nsm_wifi.py` | Working |
| **Evil Twin** | `nsm_wifi.py` | Working |
| **Wardriving** | `nsm_wifi.py` | Working |

### Network / LAN

| Module | File | Status |
|---|---|---|
| **ARP Scan** | `nsm_arp.py` | Working — LAN device discovery via ARP |
| **ARP Poison** | `nsm_arp.py` | Working — threaded ARP cache poisoning with live status |
| **LAN Discovery** | `nsm_ssdp_mdns.py` | Working — passive mDNS + SSDP device discovery with vendor categorization |
| **Telnet Bruteforce** | `nsm_telnet.py` | Working |

### Other

| Module | File | Status |
|---|---|---|
| **Flock Camera Spoofer** | `nsm_flock.py` | Working — mimics Flock ALPRs to test detection systems ([Flock-back](https://github.com/NSM-Barii/flock-back)) |

---

## Installation

```bash
git clone github.com/NSM-Barii/framework
cd framework/src

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Hardware Requirements

- **HackRF One** — Sub-GHz TX/RX (Z-Wave, 433 MHz, LoRa)
- **RTL-SDR** — passive receive-only operations (planned)
- **Bluetooth adapter** — for BLE modules
- **WiFi adapter with monitor mode** — for WiFi attacks (multiple adapters recommended)
- **macOS or Linux** — tested on macOS (Darwin) and Debian/Ubuntu

### Software Dependencies

```bash
# HackRF tools
brew install hackrf        # macOS
sudo apt install hackrf    # Debian/Ubuntu

# BLE (Linux only)
sudo apt install bluez bluez-tools libbluetooth-dev

# Evil Twin (Linux only)
sudo apt install hostapd dnsmasq

# Optional — IQ visualization
brew install inspectrum    # macOS
sudo apt install inspectrum  # Linux
```

Python dependencies (`requirements.txt`):
- `bleak` — BLE scanning and GATT operations
- `pycryptodome` — AES for Z-Wave S0 crypto
- `numpy` — IQ signal processing and FSK demodulation
- `rich` — terminal UI
- `scapy` — WiFi packet crafting

---

## Usage

```bash
sudo venv/bin/python3 main.py -h
```

### Command Prefixes

- **`-b*`** — BLE operations
- **`-w*`** — WiFi operations
- **`-z*`** — Z-Wave operations
- **`-arp-*`** — ARP operations
- **`-discover`** — LAN device discovery (mDNS/SSDP)
- **`--capture`** — SDR capture mode

### Z-Wave

```bash
# Z-Wave live recon (standalone)
sudo venv/bin/python3 nsm_zwave.py

# Z-Wave capture via main CLI
sudo venv/bin/python3 main.py -zw -t 300
```

### BLE

```bash
sudo venv/bin/python3 main.py -bs              # BLE scan
sudo venv/bin/python3 main.py -bsv -t 20      # Scan with vendor lookup
sudo venv/bin/python3 main.py -bd -m <MAC>    # Dump GATT services
sudo venv/bin/python3 main.py -bf -m <MAC>    # Fuzz all characteristics
sudo venv/bin/python3 main.py -bc -m <MAC>    # Connection spam
```

### WiFi

```bash
sudo venv/bin/python3 main.py -ws -i wlan0          # SSID scan
sudo venv/bin/python3 main.py -wc <BSSID> -i wlan0  # Client sniff
sudo venv/bin/python3 main.py -wd <BSSID>           # Deauth
sudo venv/bin/python3 main.py -we 5 --channel 6     # Evil twin
sudo venv/bin/python3 main.py -ww -i wlan0           # Wardriving
```

### ARP

```bash
sudo venv/bin/python3 main.py -arp-scan --subnet 192.168.1.0/24 -i en0          # ARP scan
sudo venv/bin/python3 main.py -arp-poison --subnet 192.168.1.0/24 --router-ip 192.168.1.1 --fake-mac 00:12:ff:12:44:12 -i en0  # Poison all
sudo venv/bin/python3 main.py -arp-poison --subnet 192.168.1.0/24 --router-ip 192.168.1.1 -m <MAC> -i en0                       # Poison target
```

### LAN Discovery

```bash
sudo venv/bin/python3 main.py -discover -i en0    # Passive mDNS + SSDP sniffing
```

### Generic Options

```
-t <seconds>      Timeout / capture duration (default: 10)
-m <MAC>          Target MAC address
-i, --iface       Network interface (default: wlan1)
--channel <n>     WiFi channel (default: 6)
--delay <seconds> Delay between repeated operations (default: 2)
--subnet <CIDR>   Target subnet (e.g. 192.168.1.0/24)
--router-ip       Router IP for ARP operations
--router-mac      Router MAC (auto-resolved if not given)
--fake-mac        Spoofed MAC for ARP poisoning (default: 00:12:ff:12:44:12)
--save            Save capture to file
--capture         SDR capture mode
```

---

## Project Structure

```
framework/
├── src/
│   ├── main.py              # CLI entry point
│   ├── nsm_vars.py          # Shared configuration and global state
│   ├── nsm_hackrf.py        # HackRF hardware layer (capture, modulate, TX)
│   ├── nsm_zwave.py         # Z-Wave passive recon + capture + demod
│   ├── nsm_ble.py           # BLE exploitation modules
│   ├── nsm_wifi.py          # WiFi attack modules
│   ├── nsm_flock.py         # Flock camera probe spoofer
│   ├── nsm_telnet.py        # Telnet bruteforce
│   ├── nsm_arp.py           # ARP scan + poison
│   ├── nsm_ssdp_mdns.py    # LAN device discovery (mDNS/SSDP)
│   ├── nsm_database.py      # File saving and database ops
│   └── requirements.txt     # Python dependencies
├── captures/                # IQ captures and recon maps
│   ├── zwave/               # Z-Wave raw IQ captures
│   ├── zwave_recon/         # Network map JSON exports
│   └── zwave_tx/            # Transmitted frame captures
├── database/                # Static data (BLE vendor OUIs, evil twin portals)
├── docs/                    # Protocol research and reference library
│   ├── ble/                 # BLE protocol fundamentals + detection notes
│   ├── wifi/                # 802.11 protocol fundamentals + detection notes
│   ├── zwave/               # Z-Wave protocol, security, and CVE references
│   ├── lan/                 # mDNS/SSDP protocol reference, LAN harvesting research, router hardening
│   └── rf/                  # RF fundamentals, modulation, jamming theory
├── _archive/                # Inactive modules and legacy code
└── README.md
```

---

## Disclaimer

This tool is for **authorized security research and penetration testing only**. Unauthorized access to devices or networks is illegal. The author is not responsible for misuse of this framework. All Z-Wave and RF research is conducted on personally owned equipment.

---

## Author

**NSM-Barii**
