# Z-WAVE CVE REFERENCE
### Compiled 2026-11-01 // NSM Barii

All CVEs confirmed via NVD, CERT/CC, or peer-reviewed research. Unverified IDs are flagged.

---

## CVE-2022-24611 — S0-No-More NonceGet DoS
**CVSS:** 6.5 Medium  
**Affected:** Silicon Labs Z-Wave 500 series (S0 and S2 devices)  
**Attack vector:** Local RF range, no auth required  

Continuous `NONCE_GET` (0x98 0x40) requests spoofed from an included-but-offline NodeID flood the nonce pool, blocking S0 and S2 handshakes for all legitimate devices on the network. ~1 frame per 2 seconds sustains the DoS. Attack ends when flooding stops.

**Implemented in:** `nsm_zwave.py` → `ZWave_DoS.nonce_flood()` / `ZWave_Frame.nonce_get_malformed()`

**Sources:**
- NVD: https://nvd.nist.gov/vuln/detail/CVE-2022-24611
- arXiv paper (S0-No-More): https://arxiv.org/pdf/2205.00781
- PT Security advisory: https://dbugs.ptsecurity.com/vulnerability/PT-2022-16760

---

## CVE-2020-9060 — Malformed Nonce/NOP DoS (500-series S2)
**CVSS:** Not listed (CERT/CC advisory)  
**Affected:** Silicon Labs 500-series, S2-enabled devices  
**Attack vector:** Local RF range  

Malformed `SECURITY_NONCE_GET`, `SECURITY_NONCE_GET_2`, `NO_OPERATION`, or NIF REQUEST messages cause denial of service and resource exhaustion on S2 devices.

**Implemented in:** `nsm_zwave.py` → `ZWave_Frame.nop()`

**Sources:**
- CERT/CC VU#142629: https://kb.cert.org/vuls/id/142629

---

## CVE-2020-9061 — Malformed Routing Message DoS (500/700-series)
**CVSS:** Not listed (CERT/CC advisory)  
**Affected:** Silicon Labs 500-series and 700-series  
**Attack vector:** Local RF range  

Malformed routing messages cause denial of service on both 500 and 700 series chipsets.

**Sources:**
- CERT/CC VU#142629: https://kb.cert.org/vuls/id/142629

---

## CVE-2020-9057 / CVE-2020-9058 / CVE-2020-10137 — Missing Auth/Encryption/Replay
**CVSS:** Not listed (CERT/CC advisory)  
**Affected:** Silicon Labs Z-Wave (various)  
**Attack vector:** Local RF range  

Protocol-level weaknesses: missing encryption enforcement, missing replay protection, missing authentication on certain command classes. These enable downgrade and injection attacks rather than direct DoS.

**Sources:**
- CERT/CC VU#142629: https://kb.cert.org/vuls/id/142629

---

## CVE-2023-0970 — Z/IP Gateway Buffer Overflow (Physical)
**CVSS:** 6.8 Medium  
**Affected:** SiLabs Z/IP Gateway SDK ≤ 7.18.01  
**Attack vector:** Physical access to Z-Wave controller  
**CWE:** CWE-120, CWE-125, CWE-787  

Multiple buffer overflow vulnerabilities allow an attacker with physical access to overwrite global memory and potentially execute arbitrary code. Fixed in Z/IP Gateway 7.18.03.

**Sources:**
- NVD: https://nvd.nist.gov/vuln/detail/CVE-2023-0970

---

## CVE-2023-0972 — Z/IP Gateway Stack Overflow (Remote RF)
**CVSS:** High (exact score not confirmed in search results)  
**Affected:** SiLabs Z/IP Gateway SDK ≤ 7.18.01  
**Attack vector:** Unauthenticated, within Z-Wave RF range  

Unauthenticated attacker in RF range can overflow a stack buffer, leading to arbitrary code execution. This is the remote-range variant of CVE-2023-0970.

**Sources:**
- NVD (referenced via related records): https://nvd.nist.gov/vuln/detail/CVE-2023-0970

---

## CVE-2023-51395 — Z-Wave End Device Stack Overflow
**CVSS:** 8.8 High  
**Affected:** Silicon Labs Z-Wave end devices (700-series), Z-Wave SDK  
**Attack vector:** Unauthenticated, within Z-Wave RF range  
**CWE:** CWE-125, CWE-787  
**⚠️ APPLICABLE — targets Z-Wave end devices (e.g. door locks)**

Unauthenticated attacker in RF range can overflow a stack buffer on a Z-Wave end device, leading to arbitrary code execution. Targets the lock directly (not the hub). No network key required. Discovered after CVE-2023-0972 which targeted controllers only.

**Implemented in:** `nsm_zwave.py` → `ZWave_DoS.end_device_overflow_fuzz()`

**Sources:**
- NVD: https://nvd.nist.gov/vuln/detail/CVE-2023-51395
- OpenCVE: https://app.opencve.io/cve/CVE-2023-51395

---

## CVE-2023-6533 — PC Controller DoS via Device Reset Locally
**CVSS:** Not confirmed  
**Affected:** Silicon Labs Z-Wave PC Controller ≤ v5.54.0  
**Attack vector:** Crafted packet  

Malformed Device Reset Locally Command Class packet causes denial-of-service-like effect on the PC Controller application.

**Sources:**
- Vulners SiLabs product list: https://vulners.com/search/vendors/silabs/products/z-wave%20pc-based%20controller

---

## CVE-2023-6640 — PC Controller Crash via Malformed S2 Nonce Get
**CVSS:** Not confirmed  
**Affected:** Silicon Labs Z-Wave PC Controller ≤ v5.54.0  
**Attack vector:** Crafted packet  

Malformed S2 Nonce Get Command Class packets crash the PC Controller.

**Implemented in:** `nsm_zwave.py` → `ZWave_Frame.s2_nonce_get_malformed()`

**Sources:**
- Vulners SiLabs product list: https://vulners.com/search/vendors/silabs/products/z-wave%20pc-based%20controller

---

## CVE-2024-22472 — 500-Series Long S0 Frame Buffer Overflow
**CVSS:** 8.1 High  
**Affected:** Silicon Labs 500-series SDK < v6.85.2  
**Attack vector:** RF range  
**CWE:** CWE-120  

Long S0 frames trigger a buffer overflow in 500-series Z-Wave devices, potentially allowing Denial of Service and Remote Code Execution. No auth required — attacker only needs RF range.

**Sources:**
- NVD: https://nvd.nist.gov/vuln/detail/CVE-2024-22472

---

## CVE-2024-50920 — Fake Node Injection via Crafted Packet
**CVSS:** 8.8 High  
**Affected:** Silicon Labs Z-Wave SDK ≤ v7.21.1 (700/800-series controllers)  
**Attack vector:** Crafted packet, RF range, no auth required  
**⚠️ APPLICABLE — targets 800-series Z-Wave controllers**

Crafted packets cause the controller to register a fake node in its node table, corrupting network state. Attacker only needs HomeID + target NodeID obtained from passive recon.

**Implemented in:** `nsm_zwave.py` → `ZWave_DoS.fake_node_inject()`

**Sources:**
- CVEdetails SiLabs list: https://www.cvedetails.com/vulnerability-list/vendor_id-20780/Silabs.html
- CNK2100 GitHub: https://github.com/CNK2100/2024-CVE/blob/main/README.md

---

## CVE-2024-50921 — Repeated Crafted Packet DoS (Controller)
**CVSS:** 6.5 Medium  
**Affected:** Silicon Labs Z-Wave SDK ≤ v7.21.1 (700/800-series controllers)  
**Attack vector:** Repeated crafted packets, RF range, no auth required  
**⚠️ APPLICABLE — targets 800-series Z-Wave controllers**

Repeated crafted packets keep the controller busy, causing denial of service. ZCOVER paper describes packets that cause the controller to search for non-existent devices indefinitely.

**Implemented in:** `nsm_zwave.py` → `ZWave_DoS.controller_dos_flood()`

**Sources:**
- CVEdetails: https://www.cvedetails.com/vulnerability-list/vendor_id-20780/Silabs.html
- CNK2100 GitHub: https://github.com/CNK2100/2024-CVE/blob/main/README.md
- ZCOVER DSN 2025: https://ssp.korea.ac.kr/assets/papers/DSN25.pdf

---

## CVE-2024-50924 — Controller↔End Device Communication Disruption
**CVSS:** 6.5 Medium  
**Affected:** Silicon Labs Z-Wave SDK ≤ v7.21.1 (700/800-series)  
**Attack vector:** Repeated crafted packets, RF range, no auth required  
**⚠️ APPLICABLE — targets 800-series Z-Wave controllers**

Repeated crafted packets disrupt communication between the controller and a specific end device. Targeted disruption of hub↔lock link without full network DoS.

**Implemented in:** `nsm_zwave.py` → `ZWave_DoS.link_disrupt()`

**Sources:**
- CVEdetails: https://www.cvedetails.com/vulnerability-list/vendor_id-20780/Silabs.html
- CNK2100 GitHub: https://github.com/CNK2100/2024-CVE/blob/main/README.md

---

## CVE-2024-50929 — Device Type Corruption via Crafted Packet
**CVSS:** 6.2 Medium  
**Affected:** Silicon Labs Z-Wave SDK ≤ v7.21.1 (700/800-series controllers)  
**Attack vector:** Crafted packet, RF range, no auth required  
**⚠️ APPLICABLE — targets 800-series Z-Wave controllers**

Crafted packet with spoofed device type causes the controller to store incorrect type info for a node, leading to routing/processing errors and DoS-like behavior.

**Implemented in:** `nsm_zwave.py` → `ZWave_DoS.device_type_corrupt()`

**Sources:**
- CVEdetails: https://www.cvedetails.com/vulnerability-list/vendor_id-20780/Silabs.html
- CNK2100 GitHub: https://github.com/CNK2100/2024-CVE/blob/main/README.md

---

## CVE-2024-50928 — Wakeup Interval Manipulation
**CVSS:** Listed on CVEdetails  
**Affected:** Silicon Labs 500-series  
**Attack vector:** Insecure permissions  

Attacker can change a sleeping end device's wakeup interval in controller memory, affecting device availability.

**Sources:**
- CVEdetails: https://www.cvedetails.com/vulnerability-list/vendor_id-20780/Silabs.html

---

## CVE-2025-10933 — Z-Wave Protocol Controller Integer Underflow / Buffer Overflow
**CVSS:** Not confirmed  
**Affected:** Z-Wave Protocol Controller  
**Attack vector:** Malformed input  
**Published:** January 2026 (NVD)  

Integer underflow leading to buffer overflow in the Z-Wave Protocol Controller, triggered by malformed input.

**Sources:**
- SentinelOne CVE DB: https://www.sentinelone.com/vulnerability-database/cve-2025-10933/

---

## ZCOVER Research — Batch of 15 Zero-Days (DSN 2025)
**CVEs assigned:** 12 new CVE IDs (includes CVE-2023-6533, -6640, -6641, -6642, -6643 and 2024 batch)  
**Affected:** Z-Wave controllers (500/700/800 series)  

Systematic fuzzing campaign uncovered 15 zero-day vulnerabilities in Z-Wave controller implementations. Findings incorporated into the 2024 Z-Wave specification update. Includes single-packet DoS keeping the controller busy searching for non-existent devices.

**Sources:**
- ZCOVER paper (DSN 2025): https://ssp.korea.ac.kr/assets/papers/DSN25.pdf

---

## Z-Shave — S0 Network Key Extraction at Inclusion
*Not a CVE — protocol design flaw disclosed by Pen Test Partners 2018.*  

Network key transmitted under all-zero temp key during inclusion. Anyone sniffing the pairing recovers the key and can decrypt all traffic + forge commands indefinitely.

**Affected:** All S0 devices (~100M chips at time of disclosure)

**Implemented in:** `src/zwave_s0.py` → `extract` mode

**Sources:**
- Pen Test Partners / The Hacker News: https://thehackernews.com/2018/05/z-wave-wireless-hacking.html
- Security Affairs: https://securityaffairs.com/72898/hacking/z-shave-z-wave-attack.html
- arXiv 2001.08497: https://arxiv.org/pdf/2001.08497

---

## S0→S2 Downgrade Attack
*Not a CVE — protocol design flaw.*  

NodeInfo frame (carrying security class advertisement) is unencrypted and unauthenticated. MITM in range during pairing can strip S2 capability and force S0 inclusion, re-enabling Z-Shave.

**Sources:**
- Pen Test Partners: https://thehackernews.com/2018/05/z-wave-wireless-hacking.html
- arXiv 2001.08497: https://arxiv.org/pdf/2001.08497
