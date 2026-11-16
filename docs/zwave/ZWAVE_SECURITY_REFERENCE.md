# Z-WAVE SECURITY & PENTEST REFERENCE
### SmartRent / Alloy smart-lock research — compiled 2026-10-27

Scope: research on **your own lock/hub on the bench**. Capturing or injecting against a
deployment you don't control (a landlord's live SmartRent system) is unauthorized access —
same techniques, different authorization.

This file collects protocol facts, the S0/S2 crypto, the known attacks, the pentest workflow,
and the tool options — tied to what we've already proven on your own capture. Sources at the end.

---

## 0. WHAT WE'VE ALREADY CONFIRMED ON THIS TARGET

- Link is **Z-Wave @ 908.42 MHz** (US), captured clean on the HackRF (100% in-band energy).
- PHY is **R2: 40 kbit/s, FSK, NRZ** — our NRZ bit-slice produced **CRC-valid frames**.
- Network: **HomeID `XX:XX:XX:XX`**, nodes observed in operation.
- A command frame is wrapped in **Security 0 (`0x98`)** — i.e. this traffic is **S0**, the weak scheme.
- Lock vs unlock are **indistinguishable by size/timing** (the difference is one encrypted byte).
- Built so far: `framework/src/zwave_capture.py` (capture+analyze), `framework/src/zwave_s0.py`
  (S0 key extraction + decrypt, crypto self-test passes).

---

## 1. Z-WAVE STACK OVERVIEW

- **Band (US):** 908.42 MHz primary. Also 916 MHz and 912 MHz for 3-channel 100 kbps.
  (EU 868.42, other regions differ.) Z-Wave Long Range (ZWLR) ~912/920 MHz is separate.
- **Standard:** ITU-T G.9959. Mesh network; one **primary controller** (the hub). In a single
  lock+hub setup the link is effectively point-to-point.
- **PHY data rates / modulation:**
  | Rate | Speed | Modulation | Coding |
  |------|-------|-----------|--------|
  | R1 | 9.6 kbps | FSK | **Manchester** |
  | R2 | 40 kbps | FSK | **NRZ**  ← our capture |
  | R3 | 100 kbps | GFSK (BT=0.6) | NRZ |
- **Frame on the air:** `preamble (0x55…) → SOF (0xF0) → MAC frame → EOF`.
- **MAC frame (R1/R2):** `HomeID[4] | SrcNodeID[1] | FrameControl[2] | Length[1] | DstNodeID[1]
  | payload (command class + data) | checksum[1]`. Checksum = XOR of the frame bytes, seed `0xFF`.

---

## 2. SECURITY 0 (S0) — THE WEAK, ATTACKABLE SCHEME

**Crypto (AES-128):**
- One **network key `K`** shared by every device in the network.
- Two subkeys derived from `K`:
  - `Kenc = AES-ECB(K, 0x55 × 16)`
  - `Kmac = AES-ECB(K, 0xAA × 16)`
- **Encryption:** AES in **OFB** mode, IV = `sender_nonce(8) ‖ receiver_nonce(8)`.
- **Auth/replay:** AES-**CBC-MAC** (first 8 bytes) + a **per-message nonce** handshake
  (`NONCE_GET` → `NONCE_REPORT`) so each encrypted command is fresh. This is why **naive
  replay fails** — the captured ciphertext is bound to a one-time nonce.

**The fatal flaw (Z-Shave):** during device **inclusion (pairing)**, the controller sends the
real network key in a `Network Key Set` frame encrypted under a **temporary key where `K` is
16 zero bytes** — a value anyone can compute. Sniff the pairing and you decrypt the key
exchange offline → recover `K` → decrypt all traffic and **forge** valid commands.

```
Kt_enc = AES-ECB(0x00×16, 0x55×16)      # fully known
Kt_mac = AES-ECB(0x00×16, 0xAA×16)      # fully known
decrypt(Network Key Set, Kt_enc)  ->  real network key K
```

`framework/src/zwave_s0.py` implements exactly this (`extract` mode), plus decrypt/MAC-verify.

---

## 3. SECURITY 2 (S2) — THE STRONG SCHEME

- **Key agreement:** Elliptic-Curve Diffie-Hellman over **Curve25519** at inclusion — no
  all-zero key, so the Z-Shave trick does **not** apply.
- **DSK (Device-Specific Key):** first 16 bytes of the node's ECDH public key, printed/QR on the
  device, entered out-of-band to authenticate the join and defeat MITM.
- **Encryption:** AES-128 **CCM**; integrity via **AES-CMAC**; replay via pre-agreed nonces (PAN)
  with next-nonce derivation.
- **Three classes, separate keys each:** S2 Access Control (door locks/garage — most trusted),
  S2 Authenticated (normal devices), S2 Unauthenticated (constrained). A compromise of a low
  class does not expose a higher class.
- Bottom line: against properly-deployed S2, there is **no known passive break** — your ceiling
  is traffic analysis (that/when, not what).

---

## 4. KNOWN VULNERABILITIES / ATTACK SURFACE

1. **Z-Shave S0 key extraction** (Pen Test Partners, 2018): all-zero temp key at inclusion leaks
   the network key to anyone sniffing the pairing. ~100M chips affected at disclosure.
2. **S2 → S0 downgrade:** the `Node Info` frame carrying the security class is sent
   **unencrypted and unauthenticated**, so an attacker in range during pairing can force a
   device that supports both down to S0, re-enabling #1. This is the key one for an S2 device.
3. **S0-No-More (2022):** a `NONCE_GET` denial-of-service abusing included-but-offline NodeIDs
   to exhaust/deny the nonce handshake.
4. **S2 implementation bugs** (not the crypto): inclusion-mode left always-open (controller
   misconfig), firmware bugs in S2 verification, side-channel on ECDH on constrained chips, and
   DSK recoverable via physical access (printed on the device).
5. **Unauthenticated/unencrypted nodes:** many non-security devices send plaintext — replay/
   inject directly.
6. **Transceiver fingerprinting / recon** (ORNL, AFIT): PHY-layer fingerprinting of Z-Wave
   modules; passive network mapping.

**For this target:** we've *observed S0 in operation*. If the lock also **includes** as S0,
#1 is a direct path. If it includes as S2, pivot to #2 (downgrade) — which only works if the
device still advertises S0 support.

---

## 5. PENTEST WORKFLOW (mapped to your gear)

```
RECON        tune 908.42 (± to 912/916), confirm bursts, map HomeID + NodeIDs      [HackRF ✓ done]
SNIFF OPS    capture operation traffic, demod to frames, read cleartext headers     [HackRF ✓ done]
             -> confirm S0 (0x98) vs S2 (0x9F) in the command class byte
CAPTURE PAIR trigger inclusion of YOUR lock, capture the whole handshake            [HackRF, capture WIDE]
             -> grab the Network Key Set encap + the matching NONCE_REPORT
EXTRACT KEY  offline: all-zero temp key -> recover network key                      [zwave_s0.py extract]
DECRYPT      decrypt captured Door Lock frames with the recovered key               [zwave_s0.py decrypt]
FORGE/INJECT NONCE_GET -> encrypt Door Lock Op Set with key -> transmit             [HackRF TX or Z-Wave stick]
```

Notes:
- **Capture the pairing WIDE.** Inclusion can negotiate rate/channel; tune center ~912 MHz and
  run a high sample rate (8–20 Msps) so you cover 908.42/912/916 at once and can't miss the
  Key Set frame. (A HackRF grabbing all three at once is actually an advantage over a 1-channel
  sniffer.)
- **Forging is interactive**, not replay: you must answer a fresh nonce each time, within the
  nonce lifetime (~seconds).

---

## 6. TOOLS

**SDR path (HackRF — RX *and* TX):**
- **EZ-Wave** (Hall & Ramsey / scriptingxss) — SDR Z-Wave toolkit: `ezstumbler` (discover),
  `ezrecon` (interrogate: mfr, device, firmware, command classes), `ezfingerprint` (PHY
  fingerprinting). Can **inject/control** devices. Built on scapy-radio's Z-Wave GNU Radio
  transceiver. Classic setup = **2× HackRF** (one RX, one TX). Old (Python2.7, GNU Radio 3.7,
  Ubuntu 14.04-era) — expect to fight the build on modern systems.
- **scapy-radio** (Bastille) — generic SDR monitor/injection; the Z-Wave PHY flowgraph EZ-Wave
  depends on.
- **URH (Universal Radio Hacker)** — best modern GUI for loading HackRF IQ, auto-FSK demod with
  proper clock recovery, reading/editing/retransmitting bits. Use this to reliably demod the
  inclusion frames before feeding `zwave_s0.py`.

**Z-Wave-radio path (easier, reliable, needed for clean TX):**
- **Silicon Labs Zniffer** — official capture tool; flash a UZB with Zniffer firmware. GUI is
  Windows-leaning (feed PTI into zniff-rs on Mac/Linux).
- **Z-Wave.Me Zniffer / A.R.T.** — cross-platform (macOS + Linux + Windows), decrypts packets
  when keys are supplied; least friction. Needs a Z-Wave.Me UZB stick.
- **zniff-rs** (Trident IoT) — open-source Rust zniffer + trace viewer; wants a Trident/PTI device.
- **Z-Wave JS / OpenZWave** — drive a controller stick as a real controller; once you hold the
  network key, the simplest way to *send* commands.

**Our own tools (this repo):**
- `framework/src/zwave_capture.py` — HackRF capture + burst/freq/in-band analysis.
- `framework/src/zwave_s0.py` — S0 key extraction (Z-Shave), decrypt, CBC-MAC verify. Needs the
  Network Key Set encap bytes + the receiver nonce from a captured inclusion.

---

## 7. HACKRF CAPABILITY — RX **AND** TX

- **RX:** proven — we demodulated CRC-valid Z-Wave R2 frames from raw HackRF IQ. No Zniffer
  needed to *receive*.
- **TX / injection:** also possible — EZ-Wave/scapy-radio transmit Z-Wave via HackRF; Hall &
  Ramsey publicly demonstrated controlling Z-Wave devices with it.
- **Caveats for TX:** half-duplex (RX then TX is fine for the sequential nonce handshake); the
  GNU Radio Z-Wave TX toolchain is old and finicky to build; USB/flowgraph latency must fit
  inside the nonce window (seconds — workable). A Z-Wave controller stick is the *easier,
  more reliable* transmitter, not a strict requirement.
- This is **transmit on the 902–928 ISM band**, not jamming. Keep it low-power and on your own
  bench device; a HackRF is not a type-accepted Part 15 radio.

---

## 8. THE CEILING, STATED HONESTLY

- Passive capture = you can see **that** a lock operation happened and **when**, plus all the
  cleartext MAC metadata (HomeID, NodeIDs, command class, S0/S2 wrapper). You **cannot** read
  or forge the encrypted command without the key.
- **S0:** the key is **obtainable** at inclusion (Z-Shave) → full decrypt + forge.
- **S2:** no known passive break; your only key paths are the **downgrade-to-S0** at pairing, a
  controller/implementation misconfig, or the **DSK via physical access**.

---

## 9. SOURCES

- Silicon Labs — Z-Wave Security whitepaper: https://silabs.com/whitepapers/z-wave-security
- Silicon Labs — INS13474 Z-Wave Security Whitepaper (PDF): https://cn.silabs.com/documents/public/white-papers/INS13474-Z-Wave-Security-Whitepaper.pdf
- Sigma Designs — SP02508 Security 2 Command Class spec (PDF): https://silabs.com/documents/public/white-papers/SP02508-Sigma-Designs-Security2-Command-Class_v2_Commercial_in_Confidence_Removed.pdf
- Pen Test Partners — Z-Shave / Z-Wave downgrade (via The Hacker News): https://thehackernews.com/2018/05/z-wave-wireless-hacking.html
- Security Affairs — Z-Shave, 100M devices: https://securityaffairs.com/72898/hacking/z-shave-z-wave-attack.html
- "An Overview of Wireless IoT Protocol Security in the Smart Home Domain" (arXiv 1801.07090): https://arxiv.org/pdf/1801.07090
- "Crushing the Wave — new Z-Wave vulnerabilities exposed" (arXiv 2001.08497): https://arxiv.org/pdf/2001.08497
- "S0-No-More: Z-Wave NonceGet DoS" (arXiv 2205.00781): https://arxiv.org/pdf/2205.00781
- EZ-Wave (SDR Z-Wave toolkit): https://github.com/scriptingxss/EZ-Wave
- scapy-radio: https://github.com/strijar/scapy-radio
- RTL-SDR — Hacking Z-Wave with a HackRF (Hall & Ramsey): https://www.rtl-sdr.com/hacking-the-z-wave-protocol-with-a-hackrf/
- Bishop Fox — Set up Zniffer for Z-Wave: https://bishopfox.com/blog/set-up-zniffer-for-z-wave
- Z-Wave.Me — Zniffer & A.R.T.: https://z-wave.me/manual/zniffer/
- zniff-rs (Trident IoT): https://github.com/tridentiot/zniff-rs
- RF Wireless World — Z-Wave PHY basics (R1/R2/R3): https://www.rfwireless-world.com/tutorials/z-wave-physical-layer-basics
- ORNL — Z-Wave network reconnaissance & transceiver fingerprinting: https://impact.ornl.gov/en/publications/z-wave-network-reconnaissance-and-transceiver-fingerprinting-usin/
- SANS — Security assessment of Z-Wave devices / replay (from handoff): https://www.giac.org/paper/gsec/35267/
- DTIC — Practical Wireless Exploitation Framework for Z-Wave (thesis, from handoff): https://apps.dtic.mil/sti/tr/pdf/AD1054454.pdf
- Z-Wave Alliance — Why SmartRent leverages Z-Wave: https://z-wavealliance.org/why-smartrent-leverages-z-wave-as-a-core-foundation-for-smart-technology-in-mdus/
