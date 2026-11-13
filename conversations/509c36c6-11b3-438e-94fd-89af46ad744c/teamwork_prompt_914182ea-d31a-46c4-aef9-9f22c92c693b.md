Research and produce a comprehensive technical implementation plan for a WhatsApp message scheduler chatbot operating within WhatsApp, enabling users to schedule messages for their contacts.

Working directory: ~/teamwork_projects/whatsapp_scheduler_bot
Integrity mode: development

## Requirements

### R1. Feasibility Analysis and Platform Architecture
Research and compare technical approaches for building a WhatsApp message scheduler chatbot operating within WhatsApp, specifically evaluating the official WhatsApp Business Platform / Cloud API versus personal account web automation/client libraries. Analyze platform constraints, message scheduling mechanisms, 24-hour customer service window restrictions, Meta policy compliance, and account ban risks for each approach.

### R2. System Design and Implementation Plan
Develop a comprehensive implementation plan and architectural specification for the chatbot. Detail the conversational user interaction flow within WhatsApp for scheduling messages (specifying recipient contact, message body, time/recurrence), the scheduling engine architecture, data persistence and job state management, recipient contact resolution, and handling edge cases such as network downtime, missed execution triggers, and session invalidation.

## Acceptance Criteria

### Platform Feasibility & Trade-Off Analysis
- [ ] The research report provides a trade-off matrix comparing the official WhatsApp Business Platform/Cloud API and web automation/client libraries across setup requirements, messaging limitations, recipient eligibility, and policy compliance risks.
- [ ] The report details the operational mechanism required for users to schedule messages to their contacts under both architectures, including template message constraints and session initiation rules.

### Architecture & Scheduling Specification
- [ ] The plan defines a complete conversational state flow or command structure for scheduling, viewing, updating, and cancelling scheduled messages within WhatsApp.
- [ ] The plan specifies the data model for scheduled messages, covering recipient identifiers, payload, scheduled execution time, status tracking, and recurrence options.
- [ ] The architecture details a persistent scheduling mechanism that guarantees reliable execution across restarts and handles failure/retry scenarios.

### Implementation Roadmap & Risk Mitigation
- [ ] The plan outlines phased implementation milestones from initial environment setup through verification and deployment.
- [ ] The plan defines concrete mitigation strategies for key failure modes: API rate limits, connection interruptions, session expiry, and time zone discrepancies.
