#!/usr/bin/env python3
"""
Independent Empirical Re-Verification Oracle for GitHub Issues & Kanban Board.
Author: teamwork_challenger_reverify
Date: 2026-11-13
"""
import json
import re
import subprocess
import sys

REPO = "Shivam-Jha96/scheduler"
PROJECT_NUM = 2
PROJECT_OWNER = "Shivam-Jha96"

CANONICAL_BO = ["BO-01", "BO-02", "BO-03", "BO-04", "BO-05", "BO-06"]
CANONICAL_BR = ["BR-01", "BR-02", "BR-03", "BR-04", "BR-05"]
CANONICAL_FR_MODULES = [
    "FR-AUTH", "FR-WIZ", "FR-CLI", "FR-SCHED", "FR-REC", "FR-REL", "FR-META"
]
CANONICAL_OMNI = [
    "OMNI-01", "OMNI-02", "OMNI-03", "OMNI-04",
    "OMNI-05", "OMNI-06", "OMNI-07", "OMNI-08"
]
CANONICAL_26_HIGH_LEVEL = (
    CANONICAL_BO + CANONICAL_BR + CANONICAL_FR_MODULES + CANONICAL_OMNI
)

CANONICAL_30_SUB_REQS = [
    "FR-AUTH-01", "FR-AUTH-02", "FR-AUTH-03", "FR-AUTH-04",
    "FR-WIZ-01", "FR-WIZ-02", "FR-WIZ-03", "FR-WIZ-04", "FR-WIZ-05",
    "FR-CLI-01", "FR-CLI-02", "FR-CLI-03", "FR-CLI-04", "FR-CLI-05", "FR-CLI-06",
    "FR-SCHED-01", "FR-SCHED-02", "FR-SCHED-03", "FR-SCHED-04",
    "FR-REC-01", "FR-REC-02", "FR-REC-03", "FR-REC-04",
    "FR-REL-01", "FR-REL-02", "FR-REL-03",
    "FR-META-01", "FR-META-02", "FR-META-03", "FR-META-04"
]

def run_command(cmd_list):
    res = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
    return res.stdout

def test_live_epics_integrity():
    print("=" * 70)
    print("STEP 1: Fetching live GitHub Issues for repository:", REPO)
    out = run_command([
        "gh", "issue", "list",
        "-R", REPO,
        "--label", "epic",
        "--state", "all",
        "--json", "number,title,labels,body,url",
        "--limit", "50"
    ])
    issues = json.loads(out)
    print(f"Total live issues fetched: {len(issues)}")
    assert len(issues) == 12, f"Expected 12 issues, found {len(issues)}"

    issues_by_number = {iss["number"]: iss for iss in issues}
    expected_numbers = set(range(1, 13))
    actual_numbers = set(issues_by_number.keys())
    assert actual_numbers == expected_numbers, f"Missing issue numbers: {expected_numbers - actual_numbers}"

    print("\nSTEP 2: Auditing Issues for Corruptions & Escaping Defects...")
    corruptions_found = []

    # Known corruption patterns to scan for
    forbidden_patterns = [
        (r"\x07|\^G", "Bell control character (^G / 0x07)"),
        (r"\b\^Gdapters", "Corrupted adapters path prefix (^Gdapters)"),
        (r"\b\^Gpps", "Corrupted apps path prefix (^Gpps)"),
        (r"<\s*/mo", "Eaten $30 variable (< /mo)"),
        (r"(?<!r)equestPairingCode", "Mangled requestPairingCode split word (missing 'r')"),
        (r"\bpm run create:adapter", "Mangled npm command (pm run)"),
        (r"\\tools/create-adapter", "Escaped backslash path (\\tools)"),
        (r"\bEPIC-1[3-8]\b", "Obsolete 18-epic scheme identifier (EPIC-13 to 18)"),
    ]

    for num in sorted(issues_by_number.keys()):
        iss = issues_by_number[num]
        body = iss["body"]
        title = iss["title"]
        issue_errors = []

        # Check raw control characters (except normal newlines and carriage returns)
        for idx, char in enumerate(body):
            code = ord(char)
            if code < 32 and code not in (9, 10, 13):
                issue_errors.append(f"Disallowed ASCII control character 0x{code:02x} at char {idx}")

        # Check regex patterns
        for pattern, desc in forbidden_patterns:
            matches = re.findall(pattern, body)
            if matches:
                issue_errors.append(f"Matched forbidden pattern '{pattern}' ({desc}): {len(matches)} occurrence(s)")

        if issue_errors:
            print(f"  ❌ Issue #{num} ({title}): FAIL")
            for err in issue_errors:
                print(f"     - {err}")
            corruptions_found.append((num, issue_errors))
        else:
            print(f"  ✓ Issue #{num}: CLEAN")

    assert len(corruptions_found) == 0, f"Found corruptions in {len(corruptions_found)} issues: {corruptions_found}"
    print("✓ All 12 issues verified 100% clean of corruptions!")

    print("\nSTEP 3: Spot-Checking Specific Remediated Issues...")
    # Issue 1
    iss1 = issues_by_number[1]["body"]
    assert "sock.requestPairingCode" in iss1, "Issue #1 missing sock.requestPairingCode"
    assert "Single-phone 8-character pairing code flow" in iss1, "Issue #1 missing pairing flow description"

    # Issue 3
    iss3 = issues_by_number[3]["body"]
    assert "< $30.00/mo" in iss3, "Issue #3 missing '< $30.00/mo'"
    assert "FR-SCHED-04" in iss3, "Issue #3 missing requirement 'FR-SCHED-04'"

    # Issue 7
    iss7 = issues_by_number[7]["body"]
    assert "tools/create-adapter" in iss7, "Issue #7 missing tools/create-adapter"
    assert "npm run create:adapter" in iss7, "Issue #7 missing npm run create:adapter"

    # Issue 8
    iss8 = issues_by_number[8]["body"]
    assert "adapters/discord" in iss8, "Issue #8 missing adapters/discord"
    assert "adapters/viber" in iss8, "Issue #8 missing adapters/viber"

    # Issue 9
    iss9 = issues_by_number[9]["body"]
    assert "adapters/signal" in iss9, "Issue #9 missing adapters/signal"
    assert "adapters/line" in iss9, "Issue #9 missing adapters/line"
    assert "adapters/imessage" in iss9, "Issue #9 missing adapters/imessage"
    assert "EPIC-13" not in iss9 and "EPIC-14" not in iss9, "Issue #9 contains obsolete epic numbers"

    # Issue 10
    iss10 = issues_by_number[10]["body"]
    assert "apps/web-dashboard" in iss10, "Issue #10 missing apps/web-dashboard"
    assert "apps/api-gateway" in iss10, "Issue #10 missing apps/api-gateway"
    assert "EPIC-15" not in iss10, "Issue #10 contains obsolete epic numbers"

    # Issue 11
    iss11 = issues_by_number[11]["body"]
    assert "< $30.00/mo" in iss11, "Issue #11 missing '< $30.00/mo'"
    assert "EPIC-18" not in iss11, "Issue #11 contains obsolete epic numbers"

    print("✓ Spot checks passed on all 7 remediated issues!")

    print("\nSTEP 4: Verifying Requirements Coverage...")
    all_text = " ".join([iss["title"] + " " + iss["body"] for iss in issues])

    # Check 26 high level
    missing_26 = [req for req in CANONICAL_26_HIGH_LEVEL if not re.search(r"\b" + re.escape(req) + r"\b", all_text)]
    print(f"High-Level Requirements (26/26): {26 - len(missing_26)}/26 covered.")
    assert len(missing_26) == 0, f"Missing high-level requirements: {missing_26}"

    # Check 30 sub-requirements
    missing_30 = [req for req in CANONICAL_30_SUB_REQS if not re.search(r"\b" + re.escape(req) + r"\b", all_text)]
    print(f"Detailed Functional Sub-Requirements (30/30): {30 - len(missing_30)}/30 covered.")
    assert len(missing_30) == 0, f"Missing functional sub-requirements: {missing_30}"
    print("✓ 100% requirements coverage verified!")

    return issues_by_number

def test_kanban_board():
    print("=" * 70)
    print("STEP 5: Auditing GitHub Project #2 Kanban Board...")
    out = run_command([
        "gh", "project", "item-list",
        str(PROJECT_NUM),
        "--owner", PROJECT_OWNER,
        "--format", "json"
    ])
    board_data = json.loads(out)
    items = board_data.get("items", [])
    print(f"Total board items: {len(items)}")
    assert len(items) == 12, f"Expected 12 board items, found {len(items)}"

    seen_numbers = set()
    for item in items:
        status = item.get("status")
        content = item.get("content", {})
        num = content.get("number")
        title = item.get("title")
        assert num is not None, f"Item has no issue number: {item}"
        seen_numbers.add(num)
        print(f"  Card #{num:2d} | Status: {status:<10} | {title}")
        assert status == "Backlog", f"Issue #{num} status is '{status}', expected 'Backlog'"

    expected_numbers = set(range(1, 13))
    assert seen_numbers == expected_numbers, f"Board missing issues: {expected_numbers - seen_numbers}"
    print("✓ All 12 Epics confirmed present and in 'Backlog' column on Kanban Project #2!")

def main():
    print("BEGINNING INDEPENDENT EMPIRICAL CHALLENGER RE-VERIFICATION")
    test_live_epics_integrity()
    test_kanban_board()
    print("\n" + "=" * 70)
    print("🎉 ALL EMPIRICAL VERIFICATION CHECKS PASSED WITH ZERO ERRORS!")
    print("DEFINITIVE VERDICT: APPROVE")
    print("=" * 70)

if __name__ == "__main__":
    main()
