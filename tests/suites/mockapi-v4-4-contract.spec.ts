import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { describe, it, expect } from 'vitest';

const payloadsPath = path.resolve(process.cwd(), 'tests/datasets/mockapi_v4_4_canonical_payloads.json');
const payloads = JSON.parse(fs.readFileSync(payloadsPath, 'utf8'));

function verifyMetaWebhookSignature(rawBody: Buffer, signatureHeader: string | undefined, appSecret: string): boolean {
  if (!signatureHeader || !signatureHeader.startsWith('sha256=')) return false;
  const providedHex = signatureHeader.slice('sha256='.length);
  const expectedHex = crypto.createHmac('sha256', appSecret).update(rawBody).digest('hex');
  const providedBuf = Buffer.from(providedHex, 'utf8');
  const expectedBuf = Buffer.from(expectedHex, 'utf8');
  if (providedBuf.length !== expectedBuf.length) return false;
  return crypto.timingSafeEqual(providedBuf, expectedBuf);
}

function isTimestampWithinReplayWindow(unixSeconds: number, nowUnixSeconds: number, maxDriftSeconds = 300): boolean {
  return Math.abs(nowUnixSeconds - unixSeconds) <= maxDriftSeconds;
}

function normalizeButtonAction(buttonId: string): { action: string; jobId?: string } {
  if (buttonId === 'BTN_CONFIRM_SENT') return { action: 'SENT_VIA_PERSONAL' };
  if (buttonId.startsWith('SENT_VIA_PERSONAL:')) {
    return { action: 'SENT_VIA_PERSONAL', jobId: buttonId.slice('SENT_VIA_PERSONAL:'.length) };
  }
  if (buttonId.startsWith('UNSUB_PAIR:')) {
    return { action: 'UNSUB_PAIR', jobId: buttonId.slice('UNSUB_PAIR:'.length) };
  }
  if (buttonId === 'UNSUB_ALL') return { action: 'UNSUB_ALL' };
  return { action: 'UNKNOWN' };
}

describe('Model C v4.4 HYBRID — MockAPI 8-Delta Contract & Meta v22.0 Templates', () => {
  it('reconciles all 8 Contract ADR deltas (6.1..6.8) and uses en_US across all 5 UTILITY templates', () => {
    expect(payloads.meta.reconciled_deltas).toEqual(['6.1', '6.2', '6.3', '6.4', '6.5', '6.6', '6.7', '6.8']);
    const templates = payloads.outbound_meta_graph_v22_templates;
    const names = Object.keys(templates);
    expect(names).toHaveLength(5);

    for (const name of names) {
      const msg = templates[name];
      expect(msg.template.language.code).toBe('en_US'); // Delta 6.1
      expect(msg.biz_opaque_callback_data).toBeTruthy();
    }
  });

  it('validates exact body params & single-trailing-suffix URL button rule (Deltas 6.2..6.5 & Erratum A.2 #4)', () => {
    const t = payloads.outbound_meta_graph_v22_templates;

    // 6.3: hybrid_notify_alice_v1 -> 3 body params
    expect(t.hybrid_notify_alice_v1.template.components[0].parameters).toHaveLength(3);

    // 6.2: hybrid_dispatch_card_v1 -> 2 body params + 1 single-suffix URL button
    expect(t.hybrid_dispatch_card_v1.template.components[0].parameters).toHaveLength(2);
    const dispatchBtn = t.hybrid_dispatch_card_v1.template.components[1];
    expect(dispatchBtn.sub_type).toBe('url');
    expect(dispatchBtn.index).toBe('0');
    expect(dispatchBtn.parameters).toHaveLength(1);
    expect(dispatchBtn.parameters[0].text).toMatch(/^\d+\?text=/);

    // 6.4: hybrid_escalation_v1 -> 2 body params (clock time) + 1 single-suffix URL button
    expect(t.hybrid_escalation_v1.template.components[0].parameters).toHaveLength(2);
    expect(t.hybrid_escalation_v1.template.components[0].parameters[1].text).toMatch(/\d{1,2}:\d{2}\s*(AM|PM)/);
    expect(t.hybrid_escalation_v1.template.components[1].parameters).toHaveLength(1);

    // Erratum A.2 #4: scheduled_relay_v1 -> {{1}} Name (Masked Phone), {{2}} Body, {{3}} First name
    const relayParams = t.scheduled_relay_v1.template.components[0].parameters;
    expect(relayParams).toHaveLength(3);
    expect(relayParams[0].text).toContain('XXX');
    expect(relayParams[0].text).not.toBe(relayParams[2].text);

    // 6.5: scheduled_cancelled_v1 -> 2 body params (Recipient, Scheduled Time)
    expect(t.scheduled_cancelled_v1.template.components[0].parameters).toHaveLength(2);
  });

  it('enforces canonical NLU, KMS, and simulation field contracts (Deltas 6.6..6.8)', () => {
    // 6.6: NLU uses raw_text and canonical 4-intent enum
    expect(payloads.nlu_parse_schedule.standard_schedule.request).toHaveProperty('raw_text');
    expect(payloads.nlu_parse_schedule.standard_schedule.request).not.toHaveProperty('message');
    expect(payloads.nlu_parse_schedule.canonical_intents).toEqual([
      'SCHEDULE_RELAY',
      'CANCEL_SCHEDULE',
      'OPT_OUT',
      'UNKNOWN'
    ]);

    // 6.7: KMS uses plaintext / ciphertext_blob / key_id (not *_b64)
    expect(payloads.kms_operations.encrypt.request).toHaveProperty('plaintext');
    expect(payloads.kms_operations.encrypt.request).not.toHaveProperty('plaintext_b64');
    expect(payloads.kms_operations.decrypt.request).toHaveProperty('ciphertext_blob');
    expect(payloads.kms_operations.decrypt.request.key_id).toBe('alias/schedulerbot-dek');

    // 6.8: Simulation uses sender_e164 / text / keyword + X-Test-Run-Id isolation
    expect(payloads.simulation_harness.isolation_headers).toHaveProperty('X-Test-Run-Id');
    expect(payloads.simulation_harness.simulate_inbound_schedule).toHaveProperty('sender_e164');
    expect(payloads.simulation_harness.simulate_opt_out).toHaveProperty('keyword');

    // 6.8: Button parser normalizes both SENT_VIA_PERSONAL:<uuid> and BTN_CONFIRM_SENT
    const uuidBtn =
      payloads.inbound_webhooks.button_confirm_personal_uuid_format.entry[0].changes[0].value.messages[0].interactive
        .button_reply.id;
    const legacyBtn =
      payloads.inbound_webhooks.button_confirm_personal_legacy_alias.entry[0].changes[0].value.messages[0].interactive
        .button_reply.id;
    expect(normalizeButtonAction(uuidBtn)).toEqual({
      action: 'SENT_VIA_PERSONAL',
      jobId: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    });
    expect(normalizeButtonAction(legacyBtn)).toEqual({ action: 'SENT_VIA_PERSONAL' });
  });

  it('TC-META-01: verifies HMAC-SHA256 timingSafeEqual length pre-check & 300s replay window guard', () => {
    const secret = 'test-meta-app-secret-v4-4';
    const rawBody = Buffer.from(JSON.stringify(payloads.inbound_webhooks.step0_alice_schedule_request), 'utf8');
    const validSig = `sha256=${crypto.createHmac('sha256', secret).update(rawBody).digest('hex')}`;

    expect(verifyMetaWebhookSignature(rawBody, validSig, secret)).toBe(true);

    // Single-byte body mutation rejected
    const tamperedBody = Buffer.from(rawBody.toString('utf8').replace('Alice', 'Malic'), 'utf8');
    expect(verifyMetaWebhookSignature(tamperedBody, validSig, secret)).toBe(false);

    // Mismatched signature length rejected safely without throwing RangeError
    expect(verifyMetaWebhookSignature(rawBody, 'sha256=deadbeef', secret)).toBe(false);
    expect(verifyMetaWebhookSignature(rawBody, undefined, secret)).toBe(false);

    // 300-second replay window guard
    expect(isTimestampWithinReplayWindow(1795500000, 1795500299)).toBe(true);
    expect(isTimestampWithinReplayWindow(1795500000, 1795500301)).toBe(false);
  });

  it('TC-META-04: covers all 6 canonical Meta Graph API error taxonomy codes', () => {
    const codes = payloads.meta_error_taxonomy.map((e: { meta_code: number }) => e.meta_code);
    expect(codes).toEqual([130429, 131056, 131047, 131051, 131026, 131031]);
  });
});
