import subprocess
import json

cmd = 'gh issue list -R Shivam-Jha96/scheduler --label epic --state all --json number,title,labels,body,url --limit 50'
issues = json.loads(subprocess.check_output(cmd, shell=True))

print("=== DEEP LINE-BY-LINE AUDIT OF LIVE GITHUB ISSUES ===")
for iss in sorted(issues, key=lambda x: x['number']):
    num = iss['number']
    title = iss['title']
    body = iss['body'] or ""
    
    issues_found = []
    
    # 1. Check control chars / non-printable chars
    for i, line in enumerate(body.splitlines(), 1):
        for char in line:
            if ord(char) < 32 and char not in ('\t', '\n', '\r'):
                issues_found.append(f"Line {i}: Control character ASCII {ord(char)} found: {repr(line)}")
                break
        if '< /mo' in line:
            issues_found.append(f"Line {i}: Broken unit economics '< /mo' (missing '$30'): {repr(line)}")
        if line.startswith('pm run'):
            issues_found.append(f"Line {i}: Broken command 'pm run' (missing 'n'): {repr(line)}")
        if r'\tools' in line:
            issues_found.append(f"Line {i}: Broken path '\\tools': {repr(line)}")
        if r'\requestPairingCode' in line:
            issues_found.append(f"Line {i}: Broken identifier '\\requestPairingCode': {repr(line)}")
            
    print(f"\nIssue #{num}: {title}")
    if issues_found:
        print(f"  ❌ {len(issues_found)} corruption(s) detected:")
        for isf in issues_found:
            print(f"     - {isf}")
    else:
        print("  ✓ Clean - no formatting/text corruption detected.")
