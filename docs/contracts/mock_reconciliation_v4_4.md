# M0-T3 Contract Reconciliation ADR — Model C v4.4 HYBRID & MockAPI_Server

> **Status**: Frozen (`M0` / Sprint 0 Gate)  
> **Baseline Specs**: `SchedulerBot Implementation Plan & Milestones v2.0` (`2026-11-24`), `BRD-FRD-WAPP-SCHED-V2.0`, `Model C v4.4 HYBRID Final Specification`

---

## 1. Resolution of All 7 Appendix A.2 Reference Errata

| Erratum # | Defect in Prior Spec | Canonical Model C v4.4 Resolution (Enforced in Code & CI) |
| :--- | :--- | :--- |
| **A.2 #1** | Sec. 6.3 heading said *"3-Tier Model"* while table defined 4 tiers | Standardized as **4-Tier Data Retention Model**: Tier 1 `<= 24h` payload shred (`E'\\x00'::bytea` + `wa_me_link = ''`), Tier 2 `90d` metadata purge/partition drop, Tier 3 `30d` logs, Tier 4 `2y` statutory consent proof. |
| **A.2 #2** | Invalid SQL cast `'\E'\\x00'::bytea'::bytea` in Sec. 7.3 Step 3 | Enforced valid PostgreSQL hex literal **`E'\\x00'::bytea`** plus **`wa_me_link = ''`** in all shred queries and CI SQL lint rules. |
| **A.2 #3** | Fig. 6 caption said *"9 discrete states"* while enum has 10 | Standardized on **10-State `scheduled_message_status` FSM**: `PENDING`, `NOTIFIED`, `FAST_TRACK`, `AWAITING_CONFIRMATION`, `DISPATCHING`, `SENT_VIA_PERSONAL`, `SENT_VIA_BOT`, `FAILED`, `CANCELLED`, `EXPIRED`. |
| **A.2 #4** | Sec. 7.3 Step 2 duplicated `senderDisplayName` into `{{1}}` and `{{3}}` and read `claimedJob.sender_name_encrypted` | Worker CAS claim MUST join `users` (`sm.user_id = u.id`), decrypt `u.sender_name_encrypted` + `u.sender_phone_encrypted` in RAM via `App_DEK`, format `{{1}}` as `Name (Masked Phone)`, `{{2}}` as plaintext `<= 500` chars (via per-message DEK), and `{{3}}` as sender first name. |
| **A.2 #5** | Sec. 8.2 `scheduler_opt_out_total` row truncated on pipe character | Locked canonical Prometheus counter: `scheduler_opt_out_total{tier="GLOBAL|PER_SENDER"}`. |
| **A.2 #6** | 8 schema/template deltas between Arch v4.4 and `MockAPI_Server` | Frozen in Section 2 below (`6.1`–`6.8`). |
| **A.2 #7** | `pg_cron` 10s Lease Reaper unconditionally incremented `retry_count` on exhausted jobs, violating `CHECK (retry_count <= max_retries)` | Enforced bounded `CASE` SQL (Section 3 below) so exhausted jobs transition to `FAILED` without exceeding `max_retries`. |

---

## 2. MockAPI_Server Reconciliation Deltas (`6.1`–`6.8`)

| ID | Component / Endpoint | Authoritative Model C v4.4 / Meta v22.0 Contract | Required Mock / CI Harness Alignment |
| :--- | :--- | :--- | :--- |
| **6.1** | **Template Locale** | `en_US` across all 5 `UTILITY` templates | Update `mock_test_data.json` fixtures from `en` to `en_US`. |
| **6.2** | **`hybrid_dispatch_card_v1`** | 2 body params (`{{1}}` Recipient, `{{2}}` `9:00 AM`) + single trailing Meta v22.0 URL button `https://wa.me/{{1}}` (`{BobE164}?text={Encoded}`) + Quick Reply `✅ I Sent It` | Reject multi-parameter URL buttons; validate single trailing URL suffix on `https://wa.me/{{1}}`. |
| **6.3** | **`hybrid_notify_alice_v1`** | 3 body params (`{{1}}` Recipient, `{{2}}` Message text, `{{3}}` `9:00 AM`) + 2 quick replies (`✏️ Edit Message`, `❌ Cancel Schedule`) | Validate 3 body parameters (updated from 2). |
| **6.4** | **`hybrid_escalation_v1`** | 2 body params (`{{1}}` Recipient, `{{2}}` clock time `9:00 AM`) + single-suffix `https://wa.me/{{1}}` URL button + 2 quick replies (`🤖 Send via Bot Now`, `✅ Already Sent`) | Expect clock time in `{{2}}` and single trailing URL suffix. |
| **6.5** | **`scheduled_cancelled_v1`** | 2 body params (`{{1}}` Recipient, `{{2}}` scheduled time `9:00 AM`) | Expect scheduled time in `{{2}}`. |
| **6.6** | **`POST /v1/parse-schedule`** | Request: `raw_text`, `timezone`; Response intent enum: `["SCHEDULE_RELAY", "CANCEL_SCHEDULE", "OPT_OUT", "UNKNOWN"]` + `validation.{is_valid, missing_fields, errors}` | Local CI mock enforces canonical v4.4 schema; any `message`/`CREATE_SCHEDULE` translation shim lives strictly inside test adapters if Modal lags. |
| **6.7** | **`POST /kms/encrypt`, `/kms/decrypt`, `/kms/generate-data-key`** | Canonical fields: `plaintext`, `ciphertext_blob`, `key_id` (`alias/schedulerbot-dek`) | Align local CI mock & test client to canonical fields (replacing `*_b64`). |
| **6.8** | **`POST /mock/simulate/*` & Button IDs** | Canonical fields `sender_e164`, `text`, `keyword`; webhook button parser accepts both `SENT_VIA_PERSONAL:<uuid>` and `BTN_CONFIRM_SENT` | Enforce per-test-run `X-Test-Run-Id` header + `POST /mock/reset` isolation so concurrent CI / `k6` runs never collide. |

---

## 3. Canonical Bounded `pg_cron` 10s Lease Reaper SQL (Erratum A.2 #7)

```sql
UPDATE scheduled_messages
SET
  status = CASE
    WHEN retry_count + 1 < max_retries THEN 'AWAITING_CONFIRMATION'::scheduled_message_status
    ELSE 'FAILED'::scheduled_message_status
  END,
  retry_count = CASE
    WHEN retry_count < max_retries THEN retry_count + 1
    ELSE retry_count
  END,
  lease_owner = NULL,
  lease_timeout_at = NULL,
  error_code = CASE
    WHEN retry_count + 1 >= max_retries AND error_code IS NULL THEN 'LEASE_RETRIES_EXHAUSTED'
    ELSE error_code
  END,
  updated_at = NOW()
WHERE status = 'DISPATCHING'
  AND lease_timeout_at < NOW();
```
