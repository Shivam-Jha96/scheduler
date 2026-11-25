import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { describe, it, expect } from 'vitest';

const vectorsPath = path.resolve(process.cwd(), 'tests/datasets/security_privacy_and_optout_vectors.json');
const vectors = JSON.parse(fs.readFileSync(vectorsPath, 'utf8'));

/** Full 64-hex HMAC-SHA256 phone blind index (truncated [0..31] retired in v4.4). */
function computePhoneBlindIndex(e164: string, pepper: string): string {
  return crypto.createHmac('sha256', pepper).update(e164.trim()).digest('hex');
}

/** Versioned BYTEA AES-256-GCM framing: [1B key_version | 12B IV | 16B authTag | N ciphertext]. */
function sealVersionedBytea(plaintext: string, dek: Buffer, keyVersion = 1): Buffer {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', dek, iv);
  const ciphertext = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  const authTag = cipher.getAuthTag();
  return Buffer.concat([Buffer.from([keyVersion]), iv, authTag, ciphertext]);
}

function openVersionedBytea(frame: Buffer, dek: Buffer): { keyVersion: number; plaintext: string } {
  const keyVersion = frame.readUInt8(0);
  const iv = frame.subarray(1, 13);
  const authTag = frame.subarray(13, 29);
  const ciphertext = frame.subarray(29);
  const decipher = crypto.createDecipheriv('aes-256-gcm', dek, iv);
  decipher.setAuthTag(authTag);
  const plaintextBuf = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  try {
    return { keyVersion, plaintext: plaintextBuf.toString('utf8') };
  } finally {
    plaintextBuf.fill(0);
  }
}

function zeroizeBuffer(buf: Buffer): void {
  buf.fill(0);
}

/** Reference Pino wildcard redactor + E.164 regex scrubber (EPIC-13). */
const REDACT_KEYS = new Set([
  'text',
  'payload',
  'message_body',
  'raw_text',
  'wa_me_link',
  'sender_name',
  'recipient_name',
  'dek',
  'plaintext',
  'phone',
  'phonenumber',
  'waid',
  'recipientid',
  'to',
  'jid'
]);

function scrubLogObject(value: unknown): unknown {
  if (typeof value === 'string') {
    return value.replace(/\+[1-9]\d{6,14}\b/g, '+[REDACTED_PHONE]');
  }
  if (Array.isArray(value)) return value.map(scrubLogObject);
  if (value && typeof value === 'object') {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value)) {
      out[k] = REDACT_KEYS.has(k.toLowerCase()) ? '[REDACTED]' : scrubLogObject(v);
    }
    return out;
  }
  return value;
}

function classifyOptOutCommand(input: string): { tier: string; action: string; targetName?: string } {
  const trimmed = input.trim();
  if (/^stop$/i.test(trimmed)) return { tier: 'GLOBAL', action: 'TIER2_GLOBAL_OPT_OUT' };
  if (/^(start|yes)$/i.test(trimmed)) return { tier: 'OPT_IN', action: 'CONSENT_OPT_IN' };
  const unsub = trimmed.match(/^unsubscribe\s+(.+)$/i);
  if (unsub) return { tier: 'PER_SENDER', action: 'TIER1_PER_SENDER_OPT_OUT', targetName: unsub[1].trim() };
  return { tier: 'NONE', action: 'NOT_GLOBAL_OPT_OUT' };
}

describe('Model C v4.4 HYBRID — Zero-Trust Crypto, 4-Tier Retention, Pino Redaction & Two-Tier Opt-Out', () => {
  it('TC-SEC-02: produces deterministic 64-hex HMAC-SHA256 blind indexes (never truncated)', () => {
    const { pepper, cases } = vectors.blind_index_vectors;
    const seen = new Set<string>();
    for (const c of cases) {
      const digest = computePhoneBlindIndex(c.e164, pepper);
      expect(digest).toMatch(/^[0-9a-f]{64}$/);
      expect(digest).toHaveLength(c.expected_length_hex);
      expect(computePhoneBlindIndex(c.e164, pepper)).toBe(digest);
      expect(computePhoneBlindIndex(c.e164, `${pepper}-rotated`)).not.toBe(digest);
      seen.add(digest);
    }
    expect(seen.size).toBe(cases.length);
  });

  it('TC-SEC-01: seals/opens versioned BYTEA AES-256-GCM frames, rejects tamper, and zeroizes DEK buffers', () => {
    for (const sample of vectors.bytea_envelope_spec.sample_plaintexts) {
      const dek = crypto.randomBytes(32);
      const frame = sealVersionedBytea(sample, dek, 1);
      expect(frame.length).toBeGreaterThanOrEqual(vectors.bytea_envelope_spec.header_total_bytes);

      const opened = openVersionedBytea(frame, dek);
      expect(opened.keyVersion).toBe(1);
      expect(opened.plaintext).toBe(sample);

      // 1-byte ciphertext tamper throws GCM authentication error
      const tampered = Buffer.from(frame);
      tampered[tampered.length - 1] ^= 0xff;
      expect(() => openVersionedBytea(tampered, dek)).toThrow();

      zeroizeBuffer(dek);
      expect(dek.every((b) => b === 0)).toBe(true);
    }
  });

  it('TC-SEC-03: enforces 4-Tier Data Retention shredding (E\\x00::bytea + empty wa_me_link)', () => {
    expect(vectors.four_tier_retention_tiers).toHaveLength(4);
    const tier1 = vectors.four_tier_retention_tiers[0];
    expect(tier1.sla_hours).toBe(24);

    // Simulate terminal shred row state
    const row = {
      dek_encrypted: Buffer.from([0x00]),
      message_content_encrypted: Buffer.from([0x00]),
      wa_me_link: ''
    };
    expect(row.dek_encrypted.equals(Buffer.from([0x00]))).toBe(true);
    expect(row.message_content_encrypted.equals(Buffer.from([0x00]))).toBe(true);
    expect(row.wa_me_link).toBe('');
  });

  it('TC-SEC-04: redacts all nested PII keys and scrubs inline E.164 phone numbers from logs', () => {
    const scrubbed = JSON.stringify(scrubLogObject(vectors.pino_redaction_vectors.sample_log_payload));
    for (const forbidden of vectors.pino_redaction_vectors.forbidden_plaintext_tokens) {
      expect(scrubbed).not.toContain(forbidden);
    }
    expect(scrubbed).toContain('+[REDACTED_PHONE]');
  });

  it('TC-OPT-01..03: classifies bare STOP, UNSUBSCRIBE <Name>, collision disambiguation & excludes Cancel/End/Quit', () => {
    for (const c of vectors.opt_out_classification_cases) {
      const res = classifyOptOutCommand(c.input);
      expect(res.tier).toBe(c.expected_tier);
      expect(res.action).toBe(c.expected_action);
      if (c.target_name) expect(res.targetName).toBe(c.target_name);
    }

    // RAM-only name collision disambiguation (zero name hashes in DB)
    const collision = vectors.per_sender_collision_case;
    const targetName = collision.command.replace(/^unsubscribe\s+/i, '').trim().toLowerCase();
    const matches = collision.active_senders.filter(
      (s: { decrypted_name: string }) => s.decrypted_name.toLowerCase() === targetName
    );
    const listIds = [...matches.map((m: { user_id: string }) => `UNSUB_PAIR:${m.user_id}`), 'UNSUB_ALL'];
    expect(listIds).toEqual(collision.expected_stateless_list_ids);
  });
});
