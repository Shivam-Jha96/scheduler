# DISPATCH for Worker 2 (Milestone 2 & 3: GitHub Repo & Projects v2 Kanban Board with Backlog Epics)
State folder: d:\Dev\repos\scheduler\.agents\teamwork\teamwork_worker_m2
Project Scope: d:\Dev\repos\scheduler\.agents\teamwork\orchestrator\PROJECT.md
Original Request: d:\Dev\repos\scheduler\.agents\teamwork\ORIGINAL_REQUEST.md
Recipe & Survey:
- d:\Dev\repos\scheduler\.agents\teamwork\teamwork_explorer_survey_3\analysis.md
- d:\Dev\repos\scheduler\.agents\teamwork\teamwork_explorer_survey_2\analysis.md


## 2026-11-13T08:53:23Z
You are a teamwork_worker assigned to execute Milestone 2 & Milestone 3: GitHub Repository Setup, GitHub Projects v2 Kanban Board Creation, and Populating all BRD Epics into the Backlog.
Working directory: d:\Dev\repos\scheduler
State folder: d:\Dev\repos\scheduler\.agents\teamwork\teamwork_worker_m2
Original Request: d:\Dev\repos\scheduler\.agents\teamwork\ORIGINAL_REQUEST.md
Project Scope: d:\Dev\repos\scheduler\.agents\teamwork\orchestrator\PROJECT.md
Explorer 3 Analysis & Recipe: d:\Dev\repos\scheduler\.agents\teamwork\teamwork_explorer_survey_3\analysis.md
Explorer 2 Requirements & Epics Catalog: d:\Dev\repos\scheduler\.agents\teamwork\teamwork_explorer_survey_2\analysis.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Tasks:
1. Read ORIGINAL_REQUEST.md, PROJECT.md, and the analyses in Explorer 3 and Explorer 2.
2. Initialize and push Git repository to GitHub:
   - Check git status. Add files: `git add .`
   - Create commit: `git commit -m "chore: initial commit of scheduler architecture, docs, and monorepo structure"`
   - Ensure branch is `master`.
   - Check if remote repo exists on GitHub (`gh repo view Shivam-Jha96/scheduler`). If not, create it:
     `gh repo create Shivam-Jha96/scheduler --public --source=. --description "Omnichannel & WhatsApp Message Scheduler Engine with Two-Tier Hybrid Architecture"`
   - Ensure remote origin is configured and push: `git push -u origin master`.
3. Check and ensure GitHub CLI token scope:
   - Check `gh auth status`.
   - If token is missing `project` scope, test if `gh project create` works. If it complains about missing `project` scope, check if a token can be refreshed (`gh auth refresh -s project`) or check environment variables or create via GitHub API.
4. Create GitHub Project (Projects v2):
   - Title: "Omnichannel Message Scheduler Kanban"
   - Command: `gh project create --owner Shivam-Jha96 --title "Omnichannel Message Scheduler Kanban" --format json`
   - Capture project number and project ID.
   - Link project to repository `Shivam-Jha96/scheduler`:
     `gh project link <projectNumber> --owner Shivam-Jha96 --repo Shivam-Jha96/scheduler`
5. Configure 5-stage Kanban Status Field via GraphQL mutation:
   - Mutate Status singleSelectOptions to:
     * "Backlog" (color: GRAY, description: "Backlog items awaiting grooming or scheduling")
     * "Ready" (color: BLUE, description: "Groomed and ready for development")
     * "In Progress" (color: YELLOW, description: "Actively in development")
     * "In Review" (color: PURPLE, description: "Under PR/code review")
     * "Done" (color: GREEN, description: "Completed and verified")
   - Use the GraphQL query tested and documented in Explorer 3's analysis (Section 4 & 7).
6. Create Labels on repository:
   - `gh label create epic --color "8A2BE2" --description "High-level Epic / BRD" --force -R Shivam-Jha96/scheduler`
   - `gh label create brd --color "0075ca" --description "Business Requirements Document specification" --force -R Shivam-Jha96/scheduler`
7. Create GitHub Issues for all BRD Epics (10 to 12 Epics covering all WhatsApp and Omnichannel BRD/FRD requirements from Explorer 2 and Explorer 3):
   - [EPIC-01] Authentication & Companion Device Pairing (FR-AUTH)
   - [EPIC-02] In-Chat Conversational Guided Wizard (FR-WIZ)
   - [EPIC-03] Command Grammar & Fast-Path Slash Interface (FR-CLI)
   - [EPIC-04] Two-Tier Hybrid Scheduling Engine (FR-SCHED)
   - [EPIC-05] Temporal Mathematics & Wall-Clock Recurrence (FR-REC)
   - [EPIC-06] Reliability, Deduplication & Anti-Ban Telemetry (FR-REL)
   - [EPIC-07] Cloud API Enterprise Model & Template Routing (FR-META)
   - [EPIC-08] Unified Transport Abstraction Layer (IMessagingTransportAdapter)
   - [EPIC-09] High-Volume Compliant Adapters (Viber & Discord)
   - [EPIC-10] Privacy & Ecosystem Bridges (Signal, LINE, iMessage)
   - [EPIC-11] Centralized Control Plane & Web Management Dashboard
   - [EPIC-12] Multi-Modal Media Storage & Pre-Warming Cache Engine
   Provide full objective, business value, requirements traceability, and acceptance criteria in the issue body.
8. Add every Epic issue to the GitHub Project and assign it to the "Backlog" status column:
   - `gh project item-add <projectNumber> --owner Shivam-Jha96 --url <issueUrl>`
   - `gh project item-edit <projectNumber> --owner Shivam-Jha96 --url <issueUrl> --field "Status" --value "Backlog"`
9. Verify all items on the board:
   - `gh project item-list <projectNumber> --owner Shivam-Jha96 --format json`
   - Verify every Epic has Status == "Backlog".
10. Write full execution details, project URLs, and verification outputs to `d:\Dev\repos\scheduler\.agents\teamwork\teamwork_worker_m2\handoff.md` and send a completion message.
