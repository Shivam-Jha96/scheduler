# Project: Omnichannel & WhatsApp Message Scheduler
# Scope: Master Project Plan & Decomposition

## Architecture
- Monorepo structure (Turborepo) with modular architecture:
  * `apps/`: Core scheduler service, API gateway, web control plane
  * `adapters/`: Transport adapters (`whatsapp-baileys`, `whatsapp-cloud`, `discord`, `viber`, `signal`, etc.)
  * `packages/`: Shared SDK (`@scheduler/adapter-sdk`), common types, database models (Prisma/PostgreSQL), queue management (BullMQ/Redis)
  * `docs/`: Central documentation repository (Boilerplate plan, HLD, LLD, BRD, FRD, Omnichannel scale-out, executive briefings)
  * `tools/`: Scaffolding CLI (`create-adapter`), test kits (`@scheduler/adapter-test-kit`)
- Two-Tier Hybrid Distributed Scheduler:
  * Tier 1: PostgreSQL 16 durable master ledger + 60s Look-Ahead Feeder (`FOR UPDATE SKIP LOCKED`)
  * Tier 2: BullMQ / Redis in-memory delayed execution queue (5-minute buffer) + Redis Redlock distributed mutex
  * Sweeper: Dead-Man's-Switch background recovery for stuck jobs

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Boilerplate Monorepo Plan Integration | Integrate monorepo boilerplate plan into docs/ with index | M1 | Survey 1 |
| 2 | Docs Hygiene & Master Index Portal | Clean obsolete drafts and generate docs/README.md portal | M1 | Survey 1 |
| 3 | GitHub Remote Repository Initialization | Initialize remote repo Shivam-Jha96/scheduler and push | M2 | Survey 3 |
| 4 | GitHub Projects v2 Kanban Creation | Create Project v2 with 5 Kanban status columns | M2 | Survey 3 |
| 5 | Status Field Customization | Configure Backlog, Ready, In Progress, In Review, Done | M2 | Survey 3 |
| 6 | Repository & Project Linkage | Link GitHub Project to repo Shivam-Jha96/scheduler | M2 | Survey 3 |
| 7 | BRD Requirements & Epics Extraction | Comprehensive extraction of all BRD/FRD specifications | M3 | Survey 2 & 3 |
| 8 | GitHub Issues Creation for Epics | Create labeled issues (epic, brd) for all BRD requirements | M3 | Survey 2 & 3 |
| 9 | Kanban Backlog Population | Add Epic issues to Project and set Status to Backlog | M3 | Survey 2 & 3 |
| 10 | Kanban Board Verification | Validate Kanban board column layout and Backlog items | M4 | Review & Audit |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Documentation Consolidation & Hygiene | Copy boilerplate plan, prune drafts, create docs/README.md index | none | DONE |
| 2 | GitHub Repository & Project Kanban Setup | Init remote repo, create Project v2, set 5 Kanban columns | M1 | DONE |
| 3 | Epics Population in Kanban Backlog | Create GitHub issues for all BRD Epics, add to Backlog | M2 | DONE |
| 4 | Review & Forensic Audit | Verification of docs, repository, board, and Backlog items | M3 | DONE |
| 5 | Preeti Recommendations Synthesis (Doc 1) | Synthesize 5 Preeti source documents into production summary | none | DONE |
| 6 | MS Teams REA Blueprint (Doc 2) | 7-layer architectural reverse engineering specification | none | DONE |
| 7 | Refined HLD & Target Stack v3.0 (Doc 3) | Quad-tier delivery, 4-step gate, canonical DDL, $8.90 OpEx | M5, M6 | DONE |
| 8 | Google Drive Cloud Synchronization | Create subfolder, upload 3 Google Docs + 3 MD files, verify | M5, M6, M7 | DONE |

## Code Layout & Write Boundaries
- Milestone 1 owns: `docs/monorepo_boilerplate_plan.md`, `docs/README.md`, `docs/whatsapp_scheduler_master_plan.md` (remove/archive), `PROJECT.md` at root.
- Milestone 2 & 3 owns: Git commits, remote push, GitHub CLI / API operations (Repository, Projects v2, Labels, Issues, Kanban Board items).
- Milestone 4: Read-only verification and test assertions.
