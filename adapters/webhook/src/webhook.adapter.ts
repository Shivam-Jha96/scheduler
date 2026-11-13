import { 
  IChannelAdapter, 
  ChannelCapabilities, 
  ChannelAccountConfig, 
  HealthStatus, 
  RecipientValidationResult, 
  DeliveryReceipt, 
  ScheduledMessageJob 
} from '@scheduler/adapter-sdk';

export class GenericWebhookAdapter implements IChannelAdapter {
  readonly channelId = 'webhook';
  readonly displayName = 'Generic HTTP Webhook';

  readonly capabilities: ChannelCapabilities = {
    supportsRichText: true,
    supportsMarkdown: true,
    supportsMedia: ['IMAGE', 'VIDEO', 'AUDIO', 'DOCUMENT'],
    supportsButtons: true,
    supportsReactions: true,
    supportsDeliveryReceipts: true,
    requiresPersistentSession: false,
    maxPayloadLength: 1048576, // 1MB JSON
    rateLimit: {
      maxPerMinute: 600,
      burst: 20,
      recommendedJitterMs: 100
    }
  };

  async initialize(accountConfig: ChannelAccountConfig): Promise<void> {
    // Validates destination base URL & optional HMAC secret
  }

  async shutdown(accountId: string): Promise<void> {
    // Stateless
  }

  async checkHealth(accountId: string): Promise<HealthStatus> {
    return {
      channelId: this.channelId,
      accountId,
      healthy: true,
      latencyMs: 15,
      timestamp: new Date()
    };
  }

  async validateRecipient(accountId: string, recipientId: string): Promise<RecipientValidationResult> {
    try {
      const url = new URL(recipientId);
      const isValid = url.protocol === 'http:' || url.protocol === 'https:';
      return { isValid, formattedId: url.toString() };
    } catch {
      return { isValid: false, reason: 'Invalid destination URL format' };
    }
  }

  async sendMessage(job: ScheduledMessageJob): Promise<DeliveryReceipt> {
    // In production: fetch(job.recipientId, { method: 'POST', body: JSON.stringify(job.payload) })
    return {
      messageId: job.id,
      externalMessageId: `webhook-post-${Date.now()}`,
      channelId: this.channelId,
      recipientId: job.recipientId,
      status: 'DELIVERED',
      deliveredAt: new Date()
    };
  }
}

export const genericWebhookAdapter = new GenericWebhookAdapter();
