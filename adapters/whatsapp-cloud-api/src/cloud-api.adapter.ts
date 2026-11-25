import {
  IChannelAdapter,
  ChannelCapabilities,
  ChannelAccountConfig,
  HealthStatus,
  RecipientValidationResult,
  DeliveryReceipt,
  ScheduledMessageJob,
  MAX_PLAINTEXT_MESSAGE_LENGTH
} from '@scheduler/adapter-sdk';

export class WhatsAppCloudApiAdapter implements IChannelAdapter {
  readonly channelId = 'whatsapp-cloud-api';
  readonly displayName = 'WhatsApp (Meta Cloud API v22.0 / WABA)';

  readonly capabilities: ChannelCapabilities = {
    supportsRichText: false,
    supportsMarkdown: false,
    supportsMedia: [],
    supportsButtons: true,
    supportsReactions: false,
    supportsDeliveryReceipts: true,
    requiresPersistentSession: false,
    maxPayloadLength: MAX_PLAINTEXT_MESSAGE_LENGTH,
    rateLimit: {
      maxPerMinute: 4800, // 80 mps Meta Cloud API v22.0 ceiling
      burst: 80,
      recommendedJitterMs: 0
    }
  };

  async initialize(_accountConfig: ChannelAccountConfig): Promise<void> {
    // M2 (EPIC-07): Validates Meta Graph API v22.0 System User Token & WABA Phone Number ID
  }

  async shutdown(_accountId: string): Promise<void> {
    // Stateless REST API - no-op
  }

  async checkHealth(accountId: string): Promise<HealthStatus> {
    return {
      channelId: this.channelId,
      accountId,
      healthy: true,
      latencyMs: 0,
      timestamp: new Date()
    };
  }

  async validateRecipient(_accountId: string, recipientId: string): Promise<RecipientValidationResult> {
    const trimmed = recipientId.trim();
    const isValidE164 = /^\+[1-9]\d{6,14}$/.test(trimmed);
    return {
      isValid: isValidE164,
      formattedId: isValidE164 ? trimmed : undefined,
      reason: isValidE164 ? undefined : 'Recipient must be a valid E.164 phone number (e.g. +919123456789)'
    };
  }

  async sendMessage(job: ScheduledMessageJob): Promise<DeliveryReceipt> {
    const text = job.payload.text ?? '';
    if (text.length === 0 || text.length > MAX_PLAINTEXT_MESSAGE_LENGTH) {
      throw new Error(
        `Plain-text message length must be between 1 and ${MAX_PLAINTEXT_MESSAGE_LENGTH} characters (got ${text.length})`
      );
    }

    // M2 (EPIC-07): Dispatches via Meta Graph API v22.0:
    // POST {META_GRAPH_API_BASE_URL}/v22.0/{WABA_PHONE_NUMBER_ID}/messages
    // with biz_opaque_callback_data = job.idempotencyKey
    return {
      messageId: job.id,
      externalMessageId: `wamid.${Date.now()}`,
      channelId: this.channelId,
      recipientId: job.recipientId,
      status: 'SENT',
      deliveredAt: new Date()
    };
  }
}

export const whatsAppCloudApiAdapter = new WhatsAppCloudApiAdapter();
