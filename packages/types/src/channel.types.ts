export enum ChannelType {
  WHATSAPP_BAILEYS = 'whatsapp-baileys',
  WHATSAPP_CLOUD_API = 'whatsapp-cloud-api',
  TELEGRAM = 'telegram',
  DISCORD = 'discord',
  SLACK = 'slack',
  SIGNAL = 'signal',
  VIBER = 'viber',
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
