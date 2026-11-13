## 🎯 Objective
Implement an interactive 5-step conversational wizard within WhatsApp chats powered by an in-memory Redis finite state machine (FSM).

## 💼 Business Value
Eliminates external app dependencies, allowing everyday users to schedule reminders in under 30 seconds directly inside WhatsApp without learning complex commands.

## 📋 Requirements Traceability
- **BRD Business Objectives**: BO-01 (In-App Scheduling), BO-04 (Dispatch Accuracy), BO-06 (Temporal Precision)
- **Functional Requirements**:
  - `FR-WIZ-01`: In-memory draft state machine with 15-minute inactivity TTL
  - `FR-WIZ-02`: Recipient resolution (vCard 3.0, E.164 phone numbers, aliases, group permissions)
  - `FR-WIZ-03`: Multi-modal payload capture (text up to 4,096 chars, images, audio/voice, documents, videos)
  - `FR-WIZ-04`: Natural language temporal parsing via `chrono-node` with user timezone anchor
  - `FR-WIZ-05`: Confirmation preview card with interactive buttons (Confirm, Edit, Cancel)

## 🛠️ Acceptance Criteria
- [ ] Inactive wizard sessions automatically expire after 15 minutes with memory reclaimed.
- [ ] Parser accepts vCard 3.0 contact cards, raw E.164 phone numbers, and saved contact aliases.
- [ ] Natural language expressions ("tomorrow at 9:30am") resolved relative to user's localized IANA timezone.
- [ ] Confirmation card renders with interactive `[✅ Confirm]`, `[✏️ Edit]`, and `[❌ Cancel]` buttons.
- [ ] Tapping `[✏️ Edit]` allows stepping back to any previous field without losing other entered data.
