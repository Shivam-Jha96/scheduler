import json
import re

# Load epics from GitHub issues
with open("scripts/project_items_verification.json", "r", encoding="utf-8-sig") as f:
    raw = json.load(f)
    board_data = raw.get("items", raw)

print(f"Board items count: {len(board_data)}")

# Requirements to check
target_reqs = {
    "BO-01": "In-App Scheduling directly via WhatsApp chat",
    "BO-02": "Zero Double-Sends (0.0% duplicate dispatches)",
    "BO-03": "Account Safety (< 0.01% ban rate)",
    "BO-04": "Dispatch Accuracy (< 1.0s timestamp variance)",
    "BO-05": "Sustainable Unit Economics (< $30/mo per 10k msgs)",
    "BO-06": "Temporal Precision & DST Invariance (0.0 min drift)",
    "BR-01": "Meta Policy & 24h Window Compliance (Utility Template fallback)",
    "BR-02": "Anti-Spam & Health Protection (pacing cadence 35-55ms/char, jitter 3-6s)",
    "BR-03": "Data Privacy & Encryption at Rest (AES-256-GCM Signal keys)",
    "BR-04": "Sender Authenticity (peer-to-peer Alice number)",
    "BR-05": "Wall-Clock Invariance (anchored to user IANA timezone)",
    "FR-AUTH": "Authentication & Companion Device Pairing",
    "FR-WIZ": "In-Chat Conversational Guided Wizard",
    "FR-CLI": "Command Grammar & Fast-Path Slash Interface",
    "FR-SCHED": "Two-Tier Hybrid Scheduling Engine",
    "FR-REC": "Temporal Mathematics & Wall-Clock Recurrence",
    "FR-REL": "Reliability, Deduplication & Anti-Ban Telemetry",
    "FR-META": "Cloud API Enterprise Model & Template Routing",
    "OMNI-01": "Transport-Agnostic Core (IMessagingTransportAdapter)",
    "OMNI-02": "Multi-Platform Sessions (user_platform_sessions)",
    "OMNI-03": "Viber Integration (REST Bot API)",
    "OMNI-04": "Discord Integration (Gateway v10)",
    "OMNI-05": "Signal Integration (signal-cli secondary device)",
    "OMNI-06": "Developer Extensibility SDK (@scheduler/adapter-sdk)",
    "OMNI-07": "Web Management Portal (Next.js)",
    "OMNI-08": "Monetization & Tier Limits (Free, Pro, Business)"
}

results = {}
for code, desc in target_reqs.items():
    matching_epics = []
    for item in board_data:
        title = item.get("title", "")
        body = item.get("content", {}).get("body", "")
        num = item.get("content", {}).get("number")
        full = f"{title}\n{body}"
        if re.search(r'\b' + re.escape(code) + r'\b', full, re.IGNORECASE):
            matching_epics.append((num, title))
    results[code] = matching_epics

print("\n--- COVERAGE SUMMARY ---")
all_covered = True
for code, desc in target_reqs.items():
    epics = results[code]
    if epics:
        epic_nums = [f"#{e[0]}" for e in epics]
        print(f"[PASS] {code:8s} : {desc[:40]:40s} -> Epics: {', '.join(epic_nums)}")
    else:
        print(f"[FAIL] {code:8s} : {desc[:40]:40s} -> NO EPIC FOUND!")
        all_covered = False

print(f"\nAll 26 Canonical Requirements Covered: {all_covered}")
