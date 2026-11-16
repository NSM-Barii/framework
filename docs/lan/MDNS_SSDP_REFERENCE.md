# mDNS & SSDP Protocol Reference
### Developed by NSM Barii

---

## mDNS (Multicast DNS)
**RFC 6762 | UDP | Port 5353 | Multicast 224.0.0.251**

### What It Is
mDNS is a zero-configuration protocol that allows devices on a local network to discover each other by name and service type without a central DNS server. Every device participates — when a device wants to find something, it multicasts a question to the entire LAN and the device that owns that name answers.

Used heavily by Apple (Bonjour), Google Chromecast, IoT devices, and is the foundation of the Matter smart home standard.

### How It Works
1. Device joins the network and multicasts an announcement: "I am `users-macbook.local` and I offer `_airplay._tcp`"
2. Other devices cache that record
3. When a device wants to find an AirPlay speaker, it multicasts: "Who has `_airplay._tcp`?"
4. The speaker responds with its IP and port
5. The requesting device connects directly — mDNS is done, application protocol takes over

### Packet Structure
mDNS uses the exact same wire format as standard DNS, wrapped in UDP.

| Field        | Value                        |
|--------------|------------------------------|
| Protocol     | UDP                          |
| Src/Dst Port | 5353                         |
| Dst IP       | 224.0.0.251 (multicast)      |
| Payload      | Standard DNS packet format   |

**Key DNS record types used:**

| Type  | Code | Purpose                                      |
|-------|------|----------------------------------------------|
| PTR   | 12   | Maps service type to instance name           |
| SRV   | 33   | Maps instance to port + target hostname      |
| A     | 1    | Maps hostname to IPv4 address                |
| AAAA  | 28   | Maps hostname to IPv6 address                |
| TXT   | 16   | Key=value metadata about the service         |

**QR Flag:**
- `QR = 0` → Query (device asking)
- `QR = 1` → Response (device answering)

### Service Naming Convention
```
_service._tcp.local
_service._udp.local
```
Example: `_airplay._tcp.local` — AirPlay service over TCP on the local domain

### Common Service Types by Brand

| Brand    | Service Type             | Purpose                        |
|----------|--------------------------|--------------------------------|
| Apple    | `_airplay._tcp`          | AirPlay video/photo streaming  |
| Apple    | `_raop._tcp`             | AirPlay audio streaming        |
| Apple    | `_homekit._tcp`          | HomeKit accessories            |
| Apple    | `_hap._tcp`              | HomeKit Accessory Protocol     |
| Apple    | `_apple-mobdev2._tcp`    | iTunes/macOS WiFi sync         |
| Google   | `_googlecast._tcp`       | Chromecast / Google Cast       |
| Amazon   | `_amzn-wplay._tcp`       | Amazon wireless audio playback |
| Roku     | `_roku-ecp._tcp`         | Roku External Control Protocol |

### After Discovery
mDNS only solves the "where are you" problem. Once a device has the IP and port, it connects directly over TCP/UDP and speaks the application protocol (AirPlay, Cast, HomeKit, IPP, etc.). mDNS plays no further role.

### Security Characteristics
- **LAN only** — routers do not forward 224.0.0.251 to the internet by default
- **No authentication** — any device on the LAN can query and receive responses
- **Passive risk** — device names often contain real user names (e.g. `Johns-iPhone.local`)
- **Spoofable** — nothing prevents a device from responding with forged records (TTL=0 sends a goodbye, evicting a device from caches)
- **Low attack surface** — mDNS itself does not allow remote control, only discovery

---

## SSDP (Simple Service Discovery Protocol)
**UPnP | UDP | Port 1900 | Multicast 239.255.255.250**

### What It Is
SSDP is the discovery layer of UPnP (Universal Plug and Play). Unlike mDNS which just finds devices, SSDP is part of a larger control framework — after discovery, UPnP allows devices to actually control each other (open router ports, send commands, etc.) with no authentication.

Used by smart TVs, Roku, Amazon Echo, Windows, gaming consoles, and older IoT devices.

### How It Works
Two main message types:

**NOTIFY** — Device proactively announces itself:
```
NOTIFY * HTTP/1.1
HOST: 239.255.255.250:1900
NT: urn:schemas-upnp-org:device:MediaRenderer:1
NTS: ssdp:alive
USN: uuid:some-uuid::urn:schemas-upnp-org:device:MediaRenderer:1
LOCATION: http://192.168.1.5:1234/description.xml
CACHE-CONTROL: max-age=1800
SERVER: Linux/4.1 UPnP/1.0 Samsung_UPnP_SDK/1.0
```

**M-SEARCH** — Device actively looks for something:
```
M-SEARCH * HTTP/1.1
HOST: 239.255.255.250:1900
MAN: "ssdp:discover"
MX: 3
ST: ssdp:all
```
Responses to M-SEARCH come back **unicast** to the requester, not multicast.

**NTS Values:**
- `ssdp:alive` — device is online and available
- `ssdp:byebye` — device is going offline (evicts from caches)

### Packet Structure

| Field    | Value                           |
|----------|---------------------------------|
| Protocol | UDP                             |
| Dst Port | 1900                            |
| Dst IP   | 239.255.255.250 (multicast)     |
| Payload  | HTTP-style plain text headers   |

**Key SSDP Headers:**

| Header         | Purpose                                          |
|----------------|--------------------------------------------------|
| NT             | Notification Type — what kind of device/service |
| NTS            | Notification Sub-Type — alive or byebye          |
| USN            | Unique Service Name — unique device identifier   |
| LOCATION       | URL to the device's full XML description         |
| SERVER         | OS + UPnP version + device SDK string            |
| CACHE-CONTROL  | How long to cache this record (seconds)          |
| ST             | Search Target — used in M-SEARCH requests        |

### Device Fingerprinting via SSDP

| Brand    | Where to Look | Keyword                        |
|----------|---------------|--------------------------------|
| Samsung  | SERVER        | `Samsung`, `urn:samsung.com`   |
| Roku     | USN           | `roku:ecp`, `uuid:roku`        |
| Google   | NT/USN        | `dial-multiscreen-org`         |
| Amazon   | USN/NT        | `amazon`, `alexa`              |

### The LOCATION URL
The `LOCATION` field points to an XML file hosted on the device that describes everything it can do — device type, manufacturer, model number, firmware version, and all available UPnP services. This is a significant privacy/security detail: connecting to that URL gives a full device profile.

### After Discovery
Unlike mDNS, SSDP is part of UPnP which includes full device control:
1. Parse `LOCATION` URL from SSDP response
2. Fetch the XML description — get full device/service info
3. Use the service URLs from the XML to send control commands
4. No authentication required at any step

### Security Characteristics
- **No authentication** — any LAN device can send UPnP commands to any other UPnP device
- **Port forwarding abuse** — UPnP allows devices to instruct your router to open ports to the internet without user consent. Widely exploited by malware.
- **CallStranger (CVE-2020-12695)** — SSDP used for SSRF and DDoS amplification against millions of devices
- **Historical CVEs** — UPnP stacks have a long history of remote code execution vulnerabilities
- **Byebye spoofing** — sending a forged `ssdp:byebye` makes devices think a target went offline

---

## mDNS vs SSDP Comparison

| Feature              | mDNS                        | SSDP                          |
|----------------------|-----------------------------|-------------------------------|
| Port                 | 5353                        | 1900                          |
| Multicast Address    | 224.0.0.251                 | 239.255.255.250               |
| Payload Format       | DNS binary                  | HTTP-style plain text         |
| Primary Use          | Name + service discovery    | Device announcement + control |
| Authentication       | None                        | None                          |
| Attack Surface       | Low (discovery only)        | High (full control framework) |
| Modern Prevalence    | High — growing              | Medium — legacy but widespread|
| Primary Ecosystem    | Apple, Google, Matter/IoT   | Smart TVs, UPnP, Windows      |
| After Discovery      | App protocol takes over     | UPnP control layer            |
