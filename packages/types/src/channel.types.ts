export enum ChannelType {
  WHATSAPP_CLOUD_API = 'whatsapp-cloud-api',
  // Phase 2+ Omnichannel Roadmap (quarantined outside Phase 1 MVP)
  VIBER = 'viber',
  DISCORD = 'discord',
  SIGNAL = 'signal',
  LINE = 'line',
  IMESSAGE = 'imessage',
  TELEGRAM = 'telegram',
  SLACK = 'slack',
  WEBHOOK = 'webhook',
  CUSTOM = 'custom'
}

export type ChannelId = string;

export interface ChannelAccountConfig {
  accountId: string;
  userId: string;
  channelId: ChannelId;
  accountIdentifier: string;
  credentials: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface HealthStatus {
  channelId: string;
  accountId: string;
  healthy: boolean;
  latencyMs: number;
  error?: string;
  timestamp: Date;
}

export interface RecipientValidationResult {
  isValid: boolean;
  formattedId?: string;
  reason?: string;
}
