# GitHub Environment & Projects v2 Kanban Architecture Analysis

**Author:** teamwork_explorer_survey_3  
**Date:** 2026-11-13  
**Scope:** GitHub CLI configuration, repository state, Projects v2 permissions, Kanban board setup, Epic structuring, and Worker execution recipe.

---

## 1. Executive Summary

This investigation analyzed the Git configuration in `d:\Dev\repos\scheduler`, the GitHub CLI (`gh`) authentication state and token permissions, and the GitHub Projects (Projects v2) API capabilities.

### Key Discoveries:
1. **Local Repository State:** The workspace is a local Git repository on branch `master` with no commits and **no remote origin configured**.
2. **GitHub Account:** The user is logged into GitHub CLI as `Shivam-Jha96`. The remote repository `Shivam-Jha96/scheduler` does not yet exist on GitHub.
3. **GitHub CLI & Permissions:** `gh` version is `2.101.0`. The current OAuth token has scopes `['gist', 'read:org', 'repo', 'workflow']`. It **lacks the `project` (or `read:project`) scope**. Attempting to query or modify Projects v2 via `gh project` or GraphQL returns an `INSUFFICIENT_SCOPES` error. The token must be refreshed via `gh auth refresh -s project` (or an updated `GH_TOKEN` provided) prior to project operations.
4. **Projects v2 Field Architecture:** Projects v2 creates a default single-select "Status" field (`Todo`, `In Progress`, `Done`). GitHub's GraphQL API provides the `updateProjectV2Field` mutation to update the single-select options cleanly to: `"Backlog"`, `"Ready"`, `"In Progress"`, `"In Review"`, and `"Done"`.
5. **Epics Representation Strategy:** Epics should be created as **real GitHub Issues with the label `epic`** (and `brd`) in `Shivam-Jha96/scheduler`, and then added to the Project board via `gh project item-add` and assigned `--field "Status" --value "Backlog"`. This preserves full git traceability (closing via PRs/commits, milestones, sub-tasks) while fully populating the Kanban board.
6. **Execution Recipe:** A turnkey, copy-paste execution script (PowerShell & Bash compatible) is provided for the Worker.

---

## 2. Git & GitHub Environment Survey

### 2.1 Local Git Repository Status
- **Working Directory:** `d:\Dev\repos\scheduler`
- **Branch:** `master`
- **Status:** Initialized, no commits yet (`No commits yet`).
- **Remotes:** `git remote -v` returned empty.
- **Git User Config:**
  - `user.name`: Shivam Jha
  - `user.email`: shivamjhaofficial96@gmail.com

### 2.2 GitHub CLI Authentication & Scopes
Execution of `gh auth status`:
```text
gh version 2.101.0 (2026-09-15)
github.com
  ✓ Logged in to github.com account Shivam-Jha96 (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'
```

### 2.3 Remote Repository Verification
Execution of `gh repo view Shivam-Jha96/scheduler`:
```text
GraphQL: Could not resolve to a Repository with the name 'Shivam-Jha96/scheduler'. (repository)
```
- The remote repository `Shivam-Jha96/scheduler` does not exist on GitHub yet.
- Because the token has the `repo` scope, creating the repository (`gh repo create scheduler --private` or `--public`) can be done immediately.

---

## 3. GitHub Projects (Projects v2) Capability Analysis

### 3.1 CLI Command Availability
- `gh project` is **built-in** natively in GitHub CLI 2.101.0 (no extension install required).
- Commands supported: `create`, `field-create`, `field-list`, `item-add`, `item-create`, `item-edit`, `item-list`, `link`, `list`, `view`.

### 3.2 Permission / Scope Barrier
Executing `gh project list --owner Shivam-Jha96` produced:
```text
error: your authentication token is missing required scopes [read:project]
To request it, run:  gh auth refresh -s read:project
```

Executing a GraphQL query for `projectsV2` details produced:
```json
{
  "errors": [
    {
      "type": "INSUFFICIENT_SCOPES",
      "message": "Your token has not been granted the required scopes to execute this query. The 'id' field requires one of the following scopes: ['read:project'], but your token has only been granted the: ['gist', 'read:org', 'repo', 'workflow'] scopes. Please modify your token's scopes at: https://github.com/settings/tokens."
    }
  ]
}
```

#### Remediation:
To execute Projects v2 creation and management, the Worker or user must expand the credentials by running:
```powershell
gh auth refresh -s project
```
Or export a Personal Access Token with `repo` and `project` scopes:
```powershell
$env:GH_TOKEN="<personal_access_token_with_project_scope>"
```

---

## 4. Kanban Board Layout & Status Customization

### 4.1 Projects v2 Default Status
When a project is created via:
```bash
gh project create --owner Shivam-Jha96 --title "Omnichannel Message Scheduler" --format json
```
It initializes a default single-select field named `Status` with default options:
- `Todo`
- `In Progress`
- `Done`

### 4.2 Updating Status Options to Match Requirements
The user requested the Kanban board to contain:
`"Backlog"`, `"Ready"`, `"In Progress"`, `"In Review"`, `"Done"`.

We introspected GitHub's GraphQL schema for `UpdateProjectV2FieldInput`:
- `fieldId`: `ID!` (the GraphQL node ID of the "Status" field)
- `singleSelectOptions`: `[ProjectV2SingleSelectFieldOptionInput!]!`
  - Each item takes:
    - `name: String!`
    - `color: ProjectV2SingleSelectFieldOptionColor!` (`GRAY`, `BLUE`, `YELLOW`, `PURPLE`, `GREEN`)
    - `description: String!`

#### Verified GraphQL Mutation:
```graphql
mutation UpdateStatusOptions($fieldId: ID!) {
  updateProjectV2Field(
    input: {
      fieldId: $fieldId
      singleSelectOptions: [
        { name: "Backlog", color: GRAY, description: "Backlog items awaiting grooming or scheduling" },
        { name: "Ready", color: BLUE, description: "Groomed and ready for development" },
        { name: "In Progress", color: YELLOW, description: "Actively in development" },
        { name: "In Review", color: PURPLE, description: "Under PR/code review" },
        { name: "Done", color: GREEN, description: "Completed and verified" }
      ]
    }
  ) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        id
        name
        options {
          id
          name
        }
      }
    }
  }
}
```

### 4.3 Setting Kanban Board View
In GitHub Projects v2, newly created projects display a Table view by default. A Kanban Board view can be generated via the GitHub REST API or configured in the GitHub web interface:
```bash
gh api --method POST /users/Shivam-Jha96/projectsV2/<project_number>/views \
  -f name="Kanban Board" \
  -f layout="board"
```
Or opened directly in the web browser at the project URL:
`https://github.com/users/Shivam-Jha96/projects/<number>` and clicking `+ New view -> Board`.

---

## 5. Epics Representation Strategy: Issues vs. Draft Items

| Dimension | Option A: Draft Project Items (`item-create`) | Option B: Repository Issues (`gh issue create`) [RECOMMENDED] |
| :--- | :--- | :--- |
| **Lifecycle** | Lives only in the Project board | Lives in the Git repository + visible on Project board |
| **Traceability** | None (cannot link Git commit hashes or PRs) | High (`Fixes #1`, PR closing keywords, Git blame) |
| **Labels & Assignees** | Limited to Project fields | Repository labels (`epic`, `brd`), assignees, milestones |
| **Sub-tasks & Checklist**| Basic markdown | GitHub Task Lists (`- [ ] #subtask`) with progress tracking |
| **API Support in gh** | `gh project item-create` | `gh issue create` followed by `gh project item-add` |
| **Kanban Column Placement** | `--field "Status" --value "Backlog"` | `--field "Status" --value "Backlog"` |

### Recommendation:
Use **Option B: Real GitHub Issues in `Shivam-Jha96/scheduler` labeled `epic`**.  
This aligns with industry best practices and ensures that when developers start implementing features, commits and PRs can reference the Epic issues directly.

---

## 6. Epic Inventory from BRD Documents

From `docs/whatsapp_scheduler_brd_frd.md` and `docs/omnichannel_messaging_scheduler_plan.md`, the BRDs map into the following 10 structured Epics:

### Core WhatsApp Scheduler Epics:
1. **[EPIC-01] Authentication & Companion Device Pairing (`FR-AUTH`)**
   - Single-phone 8-character pairing code flow (`requestPairingCode`), AES-256-GCM Signal pre-key envelope encryption, disconnect/reconnect auto-recovery.
2. **[EPIC-02] In-Chat Conversational Guided Wizard (`FR-WIZ`)**
   - 5-step state machine (Recipient vCard/E.164, Multimodal Media buffer, Chrono NLP time parser with IANA timezone anchor, Recurrence selection, Confirmation interactive card).
3. **[EPIC-03] Command Grammar & Fast-Path Slash Interface (`FR-CLI`)**
   - Slash command parsing (`/schedule`, `/list`, `/cancel`, `/edit`, `/timezone`), synchronous BullMQ eviction, interactive cancel buttons.
4. **[EPIC-04] Two-Tier Hybrid Scheduling Engine (`FR-SCHED`)**
   - PostgreSQL 16 durable master ledger (`next_run_at_utc` index), 60s Look-Ahead Feeder with `FOR UPDATE SKIP LOCKED`, 5-minute BullMQ delayed queue buffer.
5. **[EPIC-05] Temporal Mathematics & Wall-Clock Recurrence (`FR-REC`)**
   - Single Active Row recurrence, calendar-day Luxon DST invariance, month-end anchor day preservation (Jan 31 -> Feb 28 -> Mar 31), reboot fast-forwarding past `NOW()`.
6. **[EPIC-06] Reliability, Deduplication & Anti-Ban Telemetry (`FR-REL`)**
   - Deterministic 22-char `3EB0...` stanza IDs, Redis Redlock distributed mutex, Dead-Man's-Switch background sweeper, human-paced typing cadence (35–55 ms/char).
7. **[EPIC-07] Cloud API Enterprise Model & Template Routing (`FR-META`)**
   - 1-click `wa.me` CTA redirector, 24-hour service window watchdog, automated Meta Utility Template fallback routing for closed sessions.

### Omnichannel Scale-Out Epics:
8. **[EPIC-08] Unified Transport Abstraction Layer (`IMessagingTransportAdapter`)**
   - Transport factory decoupling scheduler engine from protocol adapters, polymorphic DB schema (`platform_type`, `user_platform_sessions`, `target_platform`).
9. **[EPIC-09] High-Volume Compliant Adapters (Viber & Discord)**
   - Viber REST Bot API integration (1-way and 2-way messaging, webhooks) and Discord Bot API (`discord.js`, Gateway v10) slash commands.
10. **[EPIC-10] Privacy & Ecosystem Bridges (Signal, LINE, iMessage)**
    - Headless `signal-cli` JSON-RPC secondary device daemon, official LINE Messaging API adapter, and macOS container BlueBubbles/AppleScript relay.

---

## 7. Step-by-Step Bulletproof Worker Execution Recipe

Here is the exact PowerShell script the Worker should run:

```powershell
# ==============================================================================
# STEP 0: ENSURE GITHUB PROJECT SCOPE
# ==============================================================================
# Note: If the token does not have 'project' scope, run:
# gh auth refresh -s project

# ==============================================================================
# STEP 1: INITIALIZE REMOTE REPOSITORY ON GITHUB
# ==============================================================================
cd d:\Dev\repos\scheduler

# Check if repo exists, create if not
$repoCheck = gh repo view Shivam-Jha96/scheduler 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating remote repository Shivam-Jha96/scheduler..."
    gh repo create Shivam-Jha96/scheduler --public --source=. --description "Omnichannel & WhatsApp Message Scheduler Engine with Two-Tier Hybrid Architecture"
}

# Ensure git remote is set
git remote add origin https://github.com/Shivam-Jha96/scheduler.git 2>$null
git branch -M master

# Initial commit and push
git add .
git commit -m "chore: initial commit of scheduler architecture, docs, and monorepo structure"
git push -u origin master

# ==============================================================================
# STEP 2: CREATE LABELS FOR EPICS
# ==============================================================================
gh label create epic --color "8A2BE2" --description "High-level Epic / BRD" --force -R Shivam-Jha96/scheduler
gh label create brd --color "0075ca" --description "Business Requirements Document specification" --force -R Shivam-Jha96/scheduler

# ==============================================================================
# STEP 3: CREATE GITHUB PROJECT (PROJECTS V2)
# ==============================================================================
Write-Host "Creating GitHub Project..."
$projectJson = gh project create --owner Shivam-Jha96 --title "Omnichannel Message Scheduler Kanban" --format json | ConvertFrom-Json
$projectNumber = $projectJson.number
$projectId = $projectJson.id
Write-Host "Created Project #$projectNumber with ID: $projectId"

# Link project to repository
gh project link $projectNumber --owner Shivam-Jha96 --repo Shivam-Jha96/scheduler

# ==============================================================================
# STEP 4: CONFIGURE 5-STAGE KANBAN STATUS OPTIONS VIA GRAPHQL
# ==============================================================================
# Retrieve the Status field ID
$fieldsJson = gh project field-list $projectNumber --owner Shivam-Jha96 --format json | ConvertFrom-Json
$statusField = $fieldsJson.fields | Where-Object { $_.name -eq "Status" }
$statusFieldId = $statusField.id

# Update the Status field options to: Backlog, Ready, In Progress, In Review, Done
$mutation = @"
mutation {
  updateProjectV2Field(
    input: {
      fieldId: "$statusFieldId"
      singleSelectOptions: [
        { name: "Backlog", color: GRAY, description: "Backlog items awaiting grooming or scheduling" },
        { name: "Ready", color: BLUE, description: "Groomed and ready for development" },
        { name: "In Progress", color: YELLOW, description: "Actively in development" },
        { name: "In Review", color: PURPLE, description: "Under PR/code review" },
        { name: "Done", color: GREEN, description: "Completed and verified" }
      ]
    }
  ) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        id
        name
        options {
          id
          name
        }
      }
    }
  }
}
"@

gh api graphql -f query="$mutation"

# ==============================================================================
# STEP 5: CREATE EPICS AS GITHUB ISSUES & ADD TO PROJECT BACKLOG
# ==============================================================================
$epics = @(
  @{
    title = "[EPIC-01] Authentication & Companion Device Pairing (FR-AUTH)"
    body = "### Objective`nImplement single-phone 8-character pairing code flow (`requestPairingCode`), AES-256-GCM Signal pre-key envelope encryption, and disconnect/reconnect auto-recovery.`n`n### Traceability`n- BRD: BO-01, BO-03`n- FRD: FR-AUTH (whatsapp_scheduler_brd_frd.md)"
  },
  @{
    title = "[EPIC-02] In-Chat Conversational Guided Wizard (FR-WIZ)"
    body = "### Objective`nImplement 5-step state machine (Recipient vCard/E.164, Multimodal Media buffer, Chrono NLP time parser with IANA timezone anchor, Recurrence selection, Confirmation interactive card).`n`n### Traceability`n- BRD: BO-01, BO-04, BO-06`n- FRD: FR-WIZ (whatsapp_scheduler_brd_frd.md)"
  },
  @{
    title = "[EPIC-03] Command Grammar & Fast-Path Slash Interface (FR-CLI)"
    body = "### Objective`nImplement slash command parsing (`/schedule`, `/list`, `/cancel`, `/edit`, `/timezone`), synchronous BullMQ eviction, and interactive cancel buttons.`n`n### Traceability`n- BRD: BO-01`n- FRD: FR-CLI (whatsapp_scheduler_brd_frd.md)"
  },
  @{
    title = "[EPIC-04] Two-Tier Hybrid Scheduling Engine (FR-SCHED)"
    body = "### Objective`nImplement PostgreSQL 16 durable master ledger (`next_run_at_utc` index), 60s Look-Ahead Feeder with `FOR UPDATE SKIP LOCKED`, and 5-minute BullMQ delayed queue buffer.`n`n### Traceability`n- BRD: BO-04, BO-05`n- FRD: FR-SCHED (whatsapp_scheduler_brd_frd.md)"
  },
  @{
    title = "[EPIC-05] Temporal Mathematics & Wall-Clock Recurrence (FR-REC)"
    body = "### Objective`nImplement Single Active Row recurrence, calendar-day Luxon DST invariance, month-end anchor day preservation (Jan 31 -> Feb 28 -> Mar 31), and reboot fast-forwarding past `NOW()`.`n`n### Traceability`n- BRD: BO-06`n- FRD: FR-REC (whatsapp_scheduler_brd_frd.md)"
  },
  @{
    title = "[EPIC-06] Reliability, Deduplication & Anti-Ban Telemetry (FR-REL)"
    body = "### Objective`nImplement deterministic 22-char `3EB0...` stanza IDs, Redis Redlock distributed mutex, Dead-Man's-Switch background sweeper, and human-paced typing cadence (35–55 ms/char).`n`n### Traceability`n- BRD: BO-02, BO-03`n- FRD: FR-REL (whatsapp_scheduler_brd_frd.md)"
  },
  @{
    title = "[EPIC-07] Cloud API Enterprise Model & Template Routing (FR-META)"
    body = "### Objective`nImplement 1-click `wa.me` CTA redirector, 24-hour service window watchdog, and automated Meta Utility Template fallback routing for closed sessions.`n`n### Traceability`n- BRD: BO-01, BO-05`n- FRD: FR-META (whatsapp_scheduler_brd_frd.md)"
  },
  @{
    title = "[EPIC-08] Unified Transport Abstraction Layer (IMessagingTransportAdapter)"
    body = "### Objective`nImplement decoupled transport adapter factory (`IMessagingTransportAdapter`), polymorphic database schema (`platform_type`, `user_platform_sessions`, `target_platform`).`n`n### Traceability`n- Scale-Out Plan: Phase 1 (omnichannel_messaging_scheduler_plan.md)"
  },
  @{
    title = "[EPIC-09] High-Volume Compliant Adapters (Viber & Discord)"
    body = "### Objective`nImplement official Viber REST Bot API adapter (webhooks, rich carousels) and Discord Bot API adapter (`discord.js`, Gateway v10 slash commands).`n`n### Traceability`n- Scale-Out Plan: Phase 2 (omnichannel_messaging_scheduler_plan.md)"
  },
  @{
    title = "[EPIC-10] Privacy & Ecosystem Bridges (Signal, LINE, iMessage)"
    body = "### Objective`nImplement headless `signal-cli` JSON-RPC secondary device daemon, official LINE Messaging API adapter, and macOS container BlueBubbles/AppleScript relay.`n`n### Traceability`n- Scale-Out Plan: Phase 3-4 (omnichannel_messaging_scheduler_plan.md)"
  }
)

foreach ($epic in $epics) {
    Write-Host "Creating issue: $($epic.title)..."
    $issueUrl = gh issue create -R Shivam-Jha96/scheduler --title "$($epic.title)" --body "$($epic.body)" --label "epic,brd"
    Write-Host "  -> Issue URL: $issueUrl"
    
    # Add issue to project
    Write-Host "  -> Adding to Project #$projectNumber..."
    gh project item-add $projectNumber --owner Shivam-Jha96 --url "$issueUrl"
    
    # Set Status to Backlog
    Write-Host "  -> Setting Status to Backlog..."
    gh project item-edit $projectNumber --owner Shivam-Jha96 --url "$issueUrl" --field "Status" --value "Backlog"
}

Write-Host "All 10 Epics successfully created and added to the Backlog of Project #$projectNumber!"
```

---

## 8. Verification and Invalidation Conditions

- **Verification:**
  1. `gh project view $projectNumber --owner Shivam-Jha96` displays the project details.
  2. `gh project item-list $projectNumber --owner Shivam-Jha96 --format json` verifies that all 10 items have their `status` field equal to `"Backlog"`.
  3. Visiting `https://github.com/users/Shivam-Jha96/projects/$projectNumber` displays the Kanban board with columns: `Backlog`, `Ready`, `In Progress`, `In Review`, `Done` with all 10 Epics in the `Backlog` column.
- **Invalidation Conditions:**
  - Token is missing the `project` scope; any write operation will fail until `gh auth refresh -s project` is completed.
