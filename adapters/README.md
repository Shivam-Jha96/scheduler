# Omnichannel Adapters

This directory contains pluggable channel adapters for the **Omnichannel Message Scheduler Platform**.

Every integration operates as an **independent npm workspace package** and implements the universal `IChannelAdapter` contract defined in `@scheduler/adapter-sdk`.

---

## 🚀 How to Add a New App Integration

To add a new messaging service or app integration (e.g., Signal, Viber, Line, WeChat, Twilio SMS, PagerDuty):

1. **Run the Scaffolding CLI**:
   ```bash
   npm run create:adapter -- --name <channel-slug> --display "Display Name"
   ```
   *Example*:
   ```bash
   npm run create:adapter -- --name viber --display "Viber Messenger"
   ```

2. **Implement Required Contract Methods**:
   Navigate to `adapters/<channel-slug>/src/<channel-slug>.adapter.ts`:
   - Declare static `capabilities` (rate limits, media support, formatting).
   - Implement `initialize(accountConfig)`.
   - Implement `validateRecipient(accountId, recipientId)`.
   - Implement `sendMessage(job)`.
   - (Optional) Implement `simulateActivity` for typing presence or `handleWebhook` for incoming status callbacks.

3. **Verify Compliance via the Contract Test Kit**:
   In your adapter test file, run:
   ```typescript
   import { runAdapterContractSuite } from '@scheduler/adapter-test-kit';
   import { MyAdapter } from '../src/index.js';

   await runAdapterContractSuite(new MyAdapter(), {
     mockRecipient: 'test-recipient',
     mockAccountConfig: { ... }
   });
   ```

4. **Register with the Delivery Worker**:
   Export your adapter instance in `apps/delivery-worker/src/registry.ts`.

---

## 📦 Existing Starter Adapters

| Adapter Directory | Channel ID | Protocol / Transport | Type |
| :--- | :--- | :--- | :--- |
| [`whatsapp-baileys`](file:///d:/Dev/repos/scheduler/adapters/whatsapp-baileys) | `whatsapp-baileys` | Noise_XX WebSocket | Personal Companion Device |
| [`whatsapp-cloud-api`](file:///d:/Dev/repos/scheduler/adapters/whatsapp-cloud-api) | `whatsapp-cloud-api` | Meta Graph REST API | Official Business (WABA) |
| [`telegram`](file:///d:/Dev/repos/scheduler/adapters/telegram) | `telegram` | Telegram Bot API | Official Bot |
| [`discord`](file:///d:/Dev/repos/scheduler/adapters/discord) | `discord` | Discord Gateway WebSocket (v10) | Bot Client |
| [`slack`](file:///d:/Dev/repos/scheduler/adapters/slack) | `slack` | Slack Web API / Events | Workspace App |
| [`webhook`](file:///d:/Dev/repos/scheduler/adapters/webhook) | `webhook` | HTTP POST JSON | Generic Webhook / Zapier |
