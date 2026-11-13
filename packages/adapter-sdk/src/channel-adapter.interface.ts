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
  /** Unique technical identifier matching the channel (e.g. 'whatsapp-baileys', 'telegram', 'slack') */
  readonly channelId: string;

  /** Human-readable display label */
  readonly displayName: string;

  /** Static capabilities declared by this provider */
  readonly capabilities: ChannelCapabilities;

  /** Initialize adapter instance, connect sockets, or authenticate with API */
  initialize(accountConfig: ChannelAccountConfig): Promise<void>;

  /** Gracefully terminate connection or flush session */
  shutdown(accountId: string): Promise<void>;

  /** Health probe verifying connection and credentials */
  checkHealth(accountId: string): Promise<HealthStatus>;

  /** Recipient validation (phone format, user ID, channel handle) */
  validateRecipient(accountId: string, recipientId: string): Promise<RecipientValidationResult>;

  /** Core dispatch execution */
  sendMessage(job: ScheduledMessageJob): Promise<DeliveryReceipt>;

  /** Optional: Typing simulator or online status indicator */
  simulateActivity?(accountId: string, recipientId: string, durationMs: number): Promise<void>;

  /** Optional: Inbound provider webhook processor */
  handleWebhook?(payload: unknown, headers: Record<string, string>): Promise<WebhookProcessResult>;
}
