import { describe, it, expect } from 'vitest';
import {
  ChannelType,
  ScheduledMessageStatus,
  MAX_PLAINTEXT_MESSAGE_LENGTH
} from '../packages/types/dist/index.js';
import { loadConfig } from '../packages/config/dist/index.js';
import { whatsAppCloudApiAdapter } from '../adapters/whatsapp-cloud-api/dist/index.js';
import { adapterRegistry } from '../packages/adapter-registry/dist/index.js';
import { initializeAdapters } from '../apps/delivery-worker/dist/registry.js';

describe('M0 Model C v4.4 HYBRID Baseline Guardrails', () => {
  it('defines the canonical 10-state ScheduledMessageStatus FSM (Erratum A.2 #3)', () => {
    const states = Object.values(ScheduledMessageStatus);
    expect(states).toHaveLength(10);
    expect(states).toEqual([
      'PENDING',
      'NOTIFIED',
      'FAST_TRACK',
      'AWAITING_CONFIRMATION',
      'DISPATCHING',
      'SENT_VIA_PERSONAL',
      'SENT_VIA_BOT',
      'FAILED',
      'CANCELLED',
      'EXPIRED'
    ]);
  });

  it('permanently excludes retired WHATSAPP_BAILEYS from ChannelType', () => {
    expect(Object.values(ChannelType)).not.toContain('whatsapp-baileys');
    expect(ChannelType.WHATSAPP_CLOUD_API).toBe('whatsapp-cloud-api');
  });

  it('enforces Phase 1 plain-text <= 500 char ceiling, zero media, and zero jitter on WhatsApp Cloud API v22.0', async () => {
    expect(MAX_PLAINTEXT_MESSAGE_LENGTH).toBe(500);
    expect(whatsAppCloudApiAdapter.capabilities.supportsMedia).toEqual([]);
    expect(whatsAppCloudApiAdapter.capabilities.maxPayloadLength).toBe(500);
    expect(whatsAppCloudApiAdapter.capabilities.rateLimit.recommendedJitterMs).toBe(0);

    const validRecipient = await whatsAppCloudApiAdapter.validateRecipient('acc-1', '+919123456789');
    expect(validRecipient.isValid).toBe(true);

    const invalidRecipient = await whatsAppCloudApiAdapter.validateRecipient('acc-1', 'not-a-phone');
    expect(invalidRecipient.isValid).toBe(false);

    await expect(
      whatsAppCloudApiAdapter.sendMessage({
        id: 'job-too-long',
        userId: 'user-1',
        channelAccountId: 'acc-1',
        channelId: 'whatsapp-cloud-api',
        recipientId: '+919123456789',
        payload: { text: 'a'.repeat(501) },
        scheduledFor: new Date(),
        timezone: 'Asia/Kolkata',
        idempotencyKey: 'idemp-501',
        retryCount: 0
      })
    ).rejects.toThrow(/500/);
  });

  it('loads Model C v4.4 config without Redis or static master key dependencies', () => {
    const cfg = loadConfig({});
    expect(cfg.DATABASE_URL).toContain('postgresql://');
    expect(cfg.META_GRAPH_API_VERSION).toBe('v22.0');
    expect(cfg.KMS_KEY_ID).toBe('alias/schedulerbot-dek');
    expect('REDIS_HOST' in cfg).toBe(false);
    expect('ENCRYPTION_MASTER_KEY' in cfg).toBe(false);
  });

  it('registers only Phase 1 whatsapp-cloud-api transport in delivery-worker registry', () => {
    initializeAdapters();
    const channelIds = adapterRegistry.list().map((entry) => entry.channelId);
    expect(channelIds).toContain('whatsapp-cloud-api');
    expect(channelIds).not.toContain('whatsapp-baileys');
    expect(channelIds).toHaveLength(1);
  });
});
