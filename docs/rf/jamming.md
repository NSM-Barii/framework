# RF Jamming — How It Works

## Background Noise & The Noise Floor

Every frequency has a **noise floor** — background electromagnetic interference that is always present. For a receiver to decode a signal, that signal has to be stronger than the noise floor by a certain margin. This margin is called the **Signal-to-Noise Ratio (SNR)**.

## How Jamming Works

A jammer raises that noise floor by transmitting RF energy on the same frequency. The more power transmitted, the higher the noise floor rises. Once it rises above the signal, the receiver can't distinguish the signal from the noise anymore and can't decode it. The signal is still there — it's just buried under the noise.

## True Jamming vs. Protocol Attacks

These are two completely different things operating at different layers:

**True Jamming (Physical Layer)**
- Operates at layer 1 — pure RF physics
- No frames sent, no protocol spoken
- The medium itself becomes unusable
- The receiver can't even get to the point of reading a packet

**Protocol Attacks e.g. CRC/FCS abuse (Layer 2)**
- The signal is perfectly readable
- Crafted or malformed frames cause the receiver to discard legitimate packets
- You're working inside the protocol stack
- The air is fine — the packets are the problem

## How It Applies to Flock Camera Signals

Flock cameras use three radios — each one a different frequency and a different difficulty to jam:

| Protocol | Frequency | Difficulty to Jam |
|----------|-----------|-------------------|
| WiFi     | 2.4 / 5 GHz | Moderate |
| BLE      | 2.4 GHz (hops 40 channels) | Harder — must cover full band |
| LTE      | 600 MHz – 2200 MHz | Very hard |

**Why LTE is the hardest:**
1. The camera talks to a tower potentially miles away transmitting at high power — you'd have to out-transmit the tower
2. LTE uses OFDM with aggressive error correction — it's specifically designed to survive interference and can reconstruct signals even when chunks are corrupted
3. The band is wide and spread across multiple frequencies

WiFi and BLE drown relatively easily. LTE fights back.

## Note

Jamming is illegal in the United States under 47 U.S.C. § 333 and FCC regulations. This document is for educational understanding of RF physics only.
