# DISPATCH for Explorer 3 (GitHub Environment & Projects v2 Kanban Survey)
Path: d:\Dev\repos\scheduler\.agents\teamwork\teamwork_explorer_survey_3\DISPATCH.md
Original Request: d:\Dev\repos\scheduler\.agents\teamwork\ORIGINAL_REQUEST.md

## 2026-11-13T08:38:36Z
Task:
1. Read ORIGINAL_REQUEST.md.
2. Check the git configuration in `d:\Dev\repos\scheduler`: remote URLs, branch, GitHub owner and repository name.
3. Check GitHub CLI (`gh`) authentication status (`gh auth status`) and permissions.
4. Check GitHub Projects capabilities:
   - Check if `gh project` extension/command is available.
   - Run commands (read-only queries) to check existing projects for the owner/repo (e.g. `gh project list --owner <owner>` or via `gh api graphql`).
   - Determine how to create a GitHub Project (Projects v2) with a Kanban board layout, specifically with fields/statuses such as "Backlog", "Ready", "In Progress", "In Review", "Done".
   - Determine whether Epics should be created as GitHub Issues with an "Epic" label, draft project items, or linked repository issues added to the project, and determine the exact commands to add items to the "Backlog" status column.
5. Provide a step-by-step, bulletproof execution recipe with exact `gh` CLI commands or GraphQL queries for the Worker.
6. Write your findings to `d:\Dev\repos\scheduler\.agents\teamwork\teamwork_explorer_survey_3\analysis.md` and `handoff.md`. Send a completion message when done.

