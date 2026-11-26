import subprocess
import json

out = subprocess.run(['gh', 'project', 'item-list', '2', '--owner', 'Shivam-Jha96', '--format', 'json'], capture_output=True, text=True)
items = json.loads(out.stdout)['items']
target_numbers = [14, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
found = {}
for it in items:
    num = it.get('content', {}).get('number')
    if num in target_numbers:
        found[num] = {
            'id': it.get('id'),
            'title': it.get('title'),
            'status': it.get('status'),
            'assignees': [a.get('login') if isinstance(a, dict) else str(a) for a in it.get('assignees', [])] if isinstance(it.get('assignees'), list) else str(it.get('assignees'))
        }

print(f"Total target items: {len(target_numbers)}, Found in Project #2: {len(found)}")
all_in_progress = True
for num in sorted(target_numbers):
    f = found.get(num, {})
    status = f.get('status')
    assignees = f.get('assignees')
    title = f.get('title')
    if status != 'In Progress':
        all_in_progress = False
    print(f"#{num:02d} | Status: {status} | Assignees: {assignees} | Title: {title[:75]}")

print("\nAll items in 'In Progress' status:", all_in_progress)
