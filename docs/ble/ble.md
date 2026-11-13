# Flock Safety — BLE Detection

## How They're Found

Flock BLE devices are found via **passive advertisement scanning**. The device broadcasts BLE advertisement packets that include a `Local Name` field in the GAP (Generic Access Profile) payload. That name is the detection vector.

No connection is needed. The device is continuously advertising, and flock-back reads the `local_name` from the advertisement data using `bleak` (`adv.local_name`).

## Known BLE Names

```
FS Ext Battery    # Flock Safety Extended Battery unit
Flock             # Standard Flock Safety device
Penguin           # Penguin surveillance device
Pigvision         # Pigvision surveillance system
```

Match is exact — the full `local_name` string must equal one of the above.

## Separate Hardware

BLE and WiFi Flock devices are **separate hardware**. A camera detected via WiFi probe requests will not also show up as a BLE advertisement and vice versa. Don't expect overlap when cross-referencing hits.

## Why They Advertise

BLE advertisement is the standard way a BLE peripheral announces itself before pairing or connection. These devices appear to advertise persistently — likely for configuration, status reporting, or maintenance access by Flock technicians in the field. The advertisement is not encrypted and the name is broadcast in plaintext, which is what makes passive detection possible.

## Notes

- The Raven service UUIDs in `signatures.py` (`0x3100`, `0x3200`, etc.) are a secondary signal for Raven-hardware devices. In practice, the BLE name is the primary and more reliable match.
- Scan window matters. Short scan windows will miss advertisements if the camera's advertising interval is longer than the scan. flock-back defaults to a 5-second scan window (`ble_scan_duration`), configurable with `-bs`.
- BLE detection runs on a separate thread from WiFi scanning and requires a Bluetooth adapter (`-b`, defaults to `hci0`). Use `-nb` to disable if no adapter is present.
