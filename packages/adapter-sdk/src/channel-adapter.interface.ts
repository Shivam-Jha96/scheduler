import {
  ScheduledMessageJob,
  DeliveryReceipt,
  ChannelAccountConfig,
  HealthStatus,
  RecipientValidationResult,
  WebhookProcessResult
} from '@scheduler/types';
import { ChannelCapabilities } from './capabilities.js';

export interface IChannelAdapter {
  /** Unique technical identifier matching the channel (e.g. 'whatsapp-cloud-api', 'viber', 'discord') */
  readonly channelId: string;

  /** Human-readable display label */
  readonly displayName: string;

  /** Static capabilities declared by this provider */
  readonly capabilities: ChannelCapabilities;

  /** Initialize adapter instance or verify API credentials */
  initialize(accountConfig: ChannelAccountConfig): Promise<void>;

  /** Gracefully terminate connection or flush client state */
  shutdown(accountId: string): Promise<void>;

  /** Health probe verifying connection and credentials */
  checkHealth(accountId: string): Promise<HealthStatus>;

  /** Recipient validation (E.164 phone format or channel handle) */
  validateRecipient(accountId: string, recipientId: string): Promise<RecipientValidationResult>;

  /** Core dispatch execution */
  sendMessage(job: ScheduledMessageJob): Promise<DeliveryReceipt>;

  /** Optional: Inbound provider webhook processor */
  handleWebhook?(payload: unknown, headers: Record<string, string>): Promise<WebhookProcessResult>;
}
