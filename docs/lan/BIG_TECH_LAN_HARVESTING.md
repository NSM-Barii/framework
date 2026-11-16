# Big Tech LAN Data Harvesting & Advertising
### Developed by NSM Barii
### Research compiled: 2026

---

## Overview

This document covers verified, documented cases of big tech companies using local network (LAN) data — including device discovery protocols like mDNS and SSDP — to build advertising profiles, track users, and harvest device inventory without meaningful consent. These are not conspiracy theories. They are litigated cases, academic research findings, FTC enforcement actions, and company-acknowledged practices.

---

## 1. Samsung — ACR Screen Capture Every 500ms

**What they do:**
Samsung Smart TVs run ACR (Automatic Content Recognition) software that takes a screenshot of everything on your screen every **500 milliseconds** and transmits it to Samsung's servers approximately once per minute. This happens regardless of what you're watching — live TV, streaming apps, games, or even if you're using it as a PC monitor.

The collected data is:
- Matched against a database of content to identify exactly what you're watching
- Packaged into audience segments (e.g. "sports fan", "news viewer")
- Sold to advertisers including Google and X (formerly Twitter)
- Some transmissions were sent **unencrypted in plain text**

**Opt out requires 11+ clicks** — buried deep in settings menus by design.

**Legal action:**
Texas Attorney General Ken Paxton filed suit against Samsung in December 2025 for collecting ACR data without explicit informed consent. Samsung settled in **February 2026**, agreeing to stop collecting ACR data from Texans without consent and to rewrite their privacy prompts.

**Evidence & Sources:**
- Texas AG Settlement Announcement: https://www.texasattorneygeneral.gov/news/releases/attorney-general-paxton-secures-major-agreement-samsung-ensure-texans-are-protected-smart-tvs
- Original Lawsuit: https://www.texasattorneygeneral.gov/news/releases/attorney-general-paxton-sues-five-major-tv-companies-including-some-ties-ccp-spying-texans
- Malwarebytes Coverage: https://www.malwarebytes.com/blog/news/2026/03/samsung-tvs-stop-spying-on-viewers-in-texas-heres-how-to-disable-acr-anywhere

---

## 2. LG — ACR Capture Every 10ms

**What they do:**
LG Smart TVs running WebOS use ACR that is even more aggressive than Samsung. LG captures "every sound and image" on the TV every **10 milliseconds** and transmits the data roughly every **15 seconds**. This applies to all inputs — not just LG's own apps.

**Legal action:**
Texas AG lawsuit filed December 2025. Case ongoing as of 2026.

**Evidence & Sources:**
- Texas AG Original Lawsuit (covers LG): https://www.texasattorneygeneral.gov/news/releases/attorney-general-paxton-sues-five-major-tv-companies-including-some-ties-ccp-spying-texans
- Malwarebytes Analysis: https://www.malwarebytes.com/blog/news/2026/03/samsung-tvs-stop-spying-on-viewers-in-texas-heres-how-to-disable-acr-anywhere

---

## 3. Roku — 4K ACR Snapshots Twice Per Second

**What they do:**
Roku's "Smart TV Experience" captures **4K resolution video snapshots twice per second** from all TV inputs — not just Roku channels. This data is fingerprinted against a content database and the results are shared with third-party advertisers for targeting and measurement.

Roku openly advertises this capability to advertisers on their own advertising platform page.

**What advertisers get:**
- Verified viewing data across all content sources
- Audience segments built from real viewing behavior
- Cross-device targeting capabilities

**Evidence & Sources:**
- Roku's own advertising page describing ACR capabilities: https://advertising.roku.com/learn/resources/how-advertisers-can-leverage-rokus-acr-data
- Texas AG Lawsuit: https://www.texasattorneygeneral.gov/news/releases/attorney-general-paxton-sues-five-major-tv-companies-including-some-ties-ccp-spying-texans

---

## 4. Amazon Echo — Local Network Port Scanning

**What they do:**
Amazon Echo devices were confirmed to actively **port scan other devices on your local network** to discover what else is connected. Amazon described this as finding "friends" on your network. All discovered device data was transmitted to Amazon's cloud servers.

In 2025 Amazon updated Echo to move all processing to the cloud — meaning even more data leaves your home, not less.

**Why this matters:**
An Echo sitting on your network was essentially running reconnaissance on every other device you own and reporting it back to Amazon. Combined with Amazon's advertising business, this feeds directly into household device profiling.

**Evidence & Sources:**
- Firewalla Community Documentation: https://help.firewalla.com/hc/en-us/community/posts/1500000807881-Echo-devicecs-are-port-scanning

---

## 5. Meta/Facebook — Local Port Listening to De-anonymize Browsing

**What they do:**
In 2024, academic researchers from IMDEA Networks (Madrid), Radboud University, and KU Leuven discovered that Facebook and Instagram native Android apps **silently listen on fixed local ports** on your device. Meta's tracking pixel code embedded in millions of websites communicates with these apps via WebRTC to share browser identifiers.

**The result:**
- Your incognito browsing is linked to your Facebook/Instagram account
- Browsing history is tied to a persistent identity
- Android's permission system is bypassed entirely
- Even private/incognito browser sessions are tracked

Meta removed the tracking script after the research was published — confirming the behavior was real.

**Evidence & Sources:**
- IMDEA Networks Research Paper: https://networks.imdea.org/research-co-led-by-imdea-networks-discovers-a-privacy-abuse-involving-meta-and-yandex-bridging-persistent-identifiers-to-browsing-histories/

---

## 6. Facebook iOS App — Silent LAN Scanning Before iOS 14

**What they do:**
Prior to iOS 14, the Facebook iOS app was **silently scanning your local network** for smart TVs and cast devices in the background without any user notification. The stated reason was to enable video casting — the real effect was building a map of every device in your home.

Apple's iOS 14 update introduced mandatory permission prompts for local network access. When Facebook had to ask users for permission, the behavior became visible and generated significant backlash.

**Evidence & Sources:**
- GitHub Issue on Facebook iOS SDK exposing the behavior: https://github.com/facebook/facebook-ios-sdk/issues/1469
- How-To Geek Explanation of iOS 14 Local Network Permissions: https://www.howtogeek.com/692528/why-iphone-apps-ask-for-devices-on-your-local-network/
- Apple Developer Documentation on Local Network Privacy: https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy

---

## 7. Nomi Technologies — MAC Address Retail Tracking (FTC Case)

**What they did:**
Nomi Technologies placed sensors in retail stores that detected the MAC addresses of mobile devices passively scanning for WiFi networks. They tracked approximately **9 million devices** in the first 9 months of 2013 alone — without user knowledge or consent.

The data collected:
- Foot traffic patterns
- Dwell time per location
- Repeat customer identification
- Cross-store visit tracking

Nomi claimed to offer an opt-out on their website but provided no opt-out at the physical retail locations where scanning occurred.

**FTC Enforcement:**
The FTC settled with Nomi Technologies in 2015 — the **first ever FTC enforcement action against a retail tracking company**. Nomi was prohibited from misrepresenting consumers' options for controlling data collection.

**Evidence & Sources:**
- FTC Settlement Announcement: https://www.ftc.gov/news-events/news/press-releases/2015/04/retail-tracking-firm-settles-ftc-charges-it-misled-consumers-about-opt-out-choices
- Federal Register Filing: https://www.federalregister.gov/documents/2015/05/01/2015-10154/nomi-technologies-inc-analysis-of-proposed-consent-order-to-aid-public-comment

---

## 8. Amazon Sidewalk — Opt-Out Mesh Network Using Your Bandwidth

**What it is:**
Amazon Sidewalk is a program that automatically enrolls Echo and Ring devices into a shared mesh network. Your device shares a portion of your internet bandwidth with nearby Amazon devices owned by strangers — without explicit per-use consent. It is **enabled by default**.

**Privacy implications:**
- Captures movement and activity data from multiple angles
- Enables location tracking beyond the home
- Data shared between people who have never consented to share with each other
- Tracking devices placed near your home can piggyback on your Sidewalk network

**Evidence & Sources:**
- Popular Science Analysis: https://www.popsci.com/technology/amazon-sidewalks-privacy-concerns/
- Bank Info Security Analysis: https://www.bankinfosecurity.com/amazon-sidewalk-raises-privacy-security-concerns-a-16798

---

## 9. Academic Research — "Knock and Talk" (IMC 2021)

**What researchers found:**
Georgia Tech researchers and collaborators published findings at ACM IMC 2021 showing that over **100 benign domains and 150+ malicious websites** intentionally communicate with localhost and LAN resources when you visit them in a browser.

Key findings:
- 98%+ of these requests happen within the **first 15 seconds** of page load
- WebSockets are heavily used because they are not bound by Same-Origin Policy
- Significantly more activity observed on Windows vs Linux/Mac
- Many requests probe for specific LAN device endpoints

**Evidence & Sources:**
- ACM IMC 2021 Research Paper: https://dl.acm.org/doi/10.1145/3487552.3487857

---

## 10. The Patent Trail — Documented Intent

Patents don't prove deployment but companies do not file patents for capabilities they have no interest in using.

**Google:**
- US12081411B1 — Internal network enumeration tool
- US20050097199A1 — Method and system for scanning network devices
- US20100199290A1 — System and method for multifunction device enumeration

**Intel:**
- US 8363586 — "Social networking and advertisements in mobile device on local personal area network" — explicitly describes using LAN-discovered device data for advertising

**General:**
- US 6532368 — Service advertisements in wireless local networks
- US 8296393B2 — Media advertising over peer-to-peer networks

**Source:** https://patents.google.com/

---

## 11. What Apple Did Right — iOS 14 Local Network Privacy

In iOS 14 Apple introduced a mandatory requirement that any app wanting to:
- Use mDNS/Bonjour discovery
- Scan the local network
- Make direct LAN connections

...must display a permission prompt with a plain English explanation of why. This single change exposed Facebook's silent LAN scanning, forced transparency on dozens of apps, and set a standard no other platform has matched.

**Evidence & Sources:**
- Apple Developer Documentation: https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy
- Apple Support Page: https://support.apple.com/en-us/102229

---

## Summary

| Company   | Behavior                              | Status                        |
|-----------|---------------------------------------|-------------------------------|
| Samsung   | ACR screenshots every 500ms           | Settled with Texas AG 2026    |
| LG        | ACR capture every 10ms                | Lawsuit ongoing 2026          |
| Roku      | 4K snapshots twice per second         | Lawsuit ongoing 2026          |
| Amazon    | Echo port scans your LAN              | Confirmed, no legal action    |
| Amazon    | Sidewalk mesh opt-in by default       | Active, opt-out required      |
| Meta      | Local port listening via Android apps | Removed after exposure 2024   |
| Facebook  | Silent iOS LAN scanning               | Exposed by iOS 14 prompts     |
| Nomi      | Retail MAC address tracking           | FTC settled 2015              |

---

## What You Can Do

1. **Block mDNS and SSDP at the router** — devices cannot announce themselves or discover each other
2. **Disable ACR on every smart TV** — buried in settings but findable
3. **Opt out of Amazon Sidewalk** — Alexa app → Account → Amazon Sidewalk
4. **Use a network monitor (like Ezra)** — see exactly what's talking on your LAN and where it's going
5. **VLAN segregation** — put IoT devices on a separate network with no access to your main LAN
6. **DNS blocking** — tools like Pi-hole can block known telemetry endpoints at the DNS level
