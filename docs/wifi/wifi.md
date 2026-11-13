# Flock Safety — WiFi Detection

## How They're Found

Flock cameras are detected via **probe requests**, not beacon frames. The camera is a wireless client — it scans for available networks by broadcasting probe requests on 2.4GHz and 5GHz channels. It is not acting as an access point.

The probe requests are **wildcard/null probes** — no target SSID in the request body. The camera isn't looking for a specific network name; it's scanning broadly for any available AP, which is standard client behavior before associating.

The detection vector is the **MAC address** in the transmitter address (`wlan.ta`) field of those probe frames. Match the MAC prefix against known Flock OUIs and you have a hit.

## Why Probe Requests

A camera sending wildcard probes is in scanning mode — either on first boot, reconnecting after signal loss, or doing background scanning alongside an existing association. This behavior is persistent and passive to capture. You don't need to be on the same channel as the camera's upstream AP, you just need to be on the channel the camera happens to be probing on, which rotates through channels as it scans.

## Frame Filter

```
wlan.fc.type_subtype == 0x04
```

Type `0x04` is a probe request. This is what flock-back captures via tshark in `WiFi_Sniffer`.

## Known MAC Prefixes (OUIs)

These are the OUI prefixes tied to hardware found in Flock and related devices:

```
# FS Ext Battery devices
58:8e:81   cc:cc:cc   ec:1b:bd   90:35:ea   04:0d:84
f0:82:c0   1c:34:f1   38:5b:44   94:34:69   b4:e3:f9

# Flock WiFi devices
70:c9:4e   3c:91:80   d8:f3:bc   80:30:49   14:5a:fc
74:4c:a1   08:3a:88   9c:2f:9d   94:08:53   e4:aa:ea
```

The prefix identifies the chipset vendor, not Flock directly. Flock sources hardware from multiple vendors — the OUIs reflect whatever WiFi module is in that camera generation.

## Notes

- These cameras do not beacon. You will not see them in a standard WiFi scan as an AP.
- SSID patterns (`"flock"`, `"Flock"`, etc.) in `signatures.py` exist as a secondary check but are not the primary detection path for probe-based WiFi scanning.
- Channel hopping is required to catch probes across the full spectrum since you don't know which channel the camera will probe on next.
