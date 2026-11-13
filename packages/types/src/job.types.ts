import { ChannelId } from './channel.types.js';

export enum JobStatus {
  SCHEDULED = 'SCHEDULED',
  STAGED_IN_QUEUE = 'STAGED_IN_QUEUE',
  PROCESSING = 'PROCESSING',
  DELIVERED = 'DELIVERED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED'
}

export type MediaType = 'IMAGE' | 'VIDEO' | 'AUDIO' | 'DOCUMENT';

export interface MessageMedia {
  type: MediaType;
  url: string;
  mimeType: string;
  fileName?: string;
  caption?: string;
}

export interface ScheduledMessagePayload {
  text: string;
  media?: MessageMedia[];
  metadata?: Record<string, unknown>;
}

export interface ScheduledMessageJob {
  id: string;
  userId: string;
  channelAccountId: string;
  channelId: ChannelId;
  recipientId: string;
  payload: ScheduledMessagePayload;
  scheduledFor: Date;
  timezone: string;
  cronExpression?: string;
  recurrenceRule?: string;
  parentScheduleId?: string;
  idempotencyKey: string;
  retryCount: number;
}

export interface DeliveryReceipt {
  messageId: string;
  externalMessageId?: string;
  channelId: ChannelId;
  recipientId: string;
  status: 'DELIVERED' | 'SENT' | 'FAILED';
  deliveredAt: Date;
  error?: string;
}

export interface WebhookProcessResult {
  handled: boolean;
  actionTaken?: string;
  receipt?: DeliveryReceipt;
}
