import subprocess
import json

cmd = 'gh issue list -R Shivam-Jha96/scheduler --label epic --state all --json number,title,labels,body,url --limit 50'
issues = json.loads(subprocess.check_output(cmd, shell=True))
for iss in sorted(issues, key=lambda x: x['number']):
    print('='*80)
    print(f"ISSUE #{iss['number']}: {iss['title']}")
    print(iss['body'])
    print()
