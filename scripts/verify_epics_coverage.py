import json
import subprocess
import re
import sys

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {result.stderr}")
    return result.stdout

def main():
    print("=== Empirical Adversarial Challenge: Epics Requirements Coverage ===")
    
    # 1. Fetch all epic issues from GitHub
    cmd = 'gh issue list -R Shivam-Jha96/scheduler --label epic --state all --json number,title,labels,body,url --limit 50'
    out = run_command(cmd)
    issues = json.loads(out)
    
    print(f"Total issues fetched with label 'epic': {len(issues)}")
    
    # Target Requirement Catalog
    bos = [f"BO-{i:02d}" for i in range(1, 7)]
    brs = [f"BR-{i:02d}" for i in range(1, 6)]
    fr_modules = ["FR-AUTH", "FR-WIZ", "FR-CLI", "FR-SCHED", "FR-REC", "FR-REL", "FR-META"]
    omnis = [f"OMNI-{i:02d}" for i in range(1, 9)]
    
    # Sub-requirements extracted from BRD/FRD
    fr_subreqs = {
        "FR-AUTH": [f"FR-AUTH-{i:02d}" for i in range(1, 5)],
        "FR-WIZ": [f"FR-WIZ-{i:02d}" for i in range(1, 6)], # check 06 too
        "FR-CLI": [f"FR-CLI-{i:02d}" for i in range(1, 7)],
        "FR-SCHED": [f"FR-SCHED-{i:02d}" for i in range(1, 5)],
        "FR-REC": [f"FR-REC-{i:02d}" for i in range(1, 5)],
        "FR-REL": [f"FR-REL-{i:02d}" for i in range(1, 4)],
        "FR-META": [f"FR-META-{i:02d}" for i in range(1, 5)],
    }
    
    # Store mappings
    issue_data = {}
    req_to_epics = {}
    
    all_requirements = set(bos + brs + omnis)
    for subs in fr_subreqs.values():
        all_requirements.update(subs)
    for mod in fr_modules:
        all_requirements.add(mod)
        
    for req in all_requirements:
        req_to_epics[req] = []

    for issue in issues:
        num = issue["number"]
        title = issue["title"]
        body = issue["body"] or ""
        url = issue["url"]
        labels = [l["name"] for l in issue.get("labels", [])]
        
        issue_data[num] = {
            "title": title,
            "url": url,
            "labels": labels,
            "body": body,
            "body_length": len(body),
            "found_reqs": set()
        }
        
        full_text = f"{title}\n{body}"
        
        # Search for each requirement
        for req in all_requirements:
            # Match word boundary or exact token
            pattern = r'\b' + re.escape(req) + r'\b'
            if re.search(pattern, full_text, re.IGNORECASE):
                req_to_epics[req].append(num)
                issue_data[num]["found_reqs"].add(req)

    print("\n--- EPICS INVENTORY ---")
    for num in sorted(issue_data.keys()):
        d = issue_data[num]
        print(f"#{num}: {d['title']} | Body Length: {d['body_length']} chars | Labels: {d['labels']}")
        matched = sorted(list(d["found_reqs"]))
        print(f"   Matched Requirements: {matched}\n")

    print("\n--- REQUIREMENT COVERAGE AUDIT ---")
    
    def check_category(name, req_list):
        print(f"\n[Category: {name}]")
        missing = []
        covered = []
        for r in req_list:
            epics = req_to_epics.get(r, [])
            if epics:
                print(f"  ✓ {r:12s} -> Covered in Epics: {epics}")
                covered.append(r)
            else:
                print(f"  ✗ {r:12s} -> NOT FOUND IN ANY EPIC!")
                missing.append(r)
        return covered, missing

    cov_bo, miss_bo = check_category("Business Objectives (BO-01 to BO-06)", bos)
    cov_br, miss_br = check_category("Business Rules (BR-01 to BR-05)", brs)
    cov_mod, miss_mod = check_category("Functional Modules (FR-AUTH to FR-META)", fr_modules)
    cov_omni, miss_omni = check_category("Omnichannel Scale-Out (OMNI-01 to OMNI-08)", omnis)

    all_fr_subs = []
    for subs in fr_subreqs.values():
        all_fr_subs.extend(subs)
    cov_subs, miss_subs = check_category("Functional Sub-Requirements (FR-*-0X)", all_fr_subs)

    print("\n================ SUMMARY ================")
    print(f"BO Coverage:   {len(cov_bo)}/{len(bos)} (Missing: {miss_bo})")
    print(f"BR Coverage:   {len(cov_br)}/{len(brs)} (Missing: {miss_br})")
    print(f"FR Modules:    {len(cov_mod)}/{len(fr_modules)} (Missing: {miss_mod})")
    print(f"OMNI Coverage: {len(cov_omni)}/{len(omnis)} (Missing: {miss_omni})")
    print(f"FR Detailed:   {len(cov_subs)}/{len(all_fr_subs)} (Missing: {miss_subs})")
    
    total_expected = len(bos) + len(brs) + len(fr_modules) + len(omnis)
    total_covered = len(cov_bo) + len(cov_br) + len(cov_mod) + len(cov_omni)
    print(f"\nHigh-Level Target Coverage: {total_covered}/{total_expected} ({total_covered/total_expected*100:.1f}%)")

if __name__ == "__main__":
    main()
