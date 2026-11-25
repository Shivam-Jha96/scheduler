import { ChannelId } from './channel.types.js';

/**
 * Canonical 10-State Finite State Machine for Model C v4.4 HYBRID.
 * Mirrors PostgreSQL `scheduled_message_status` enum (Erratum A.2 #3).
 */
export enum ScheduledMessageStatus {
  PENDING = 'PENDING',
  NOTIFIED = 'NOTIFIED',
  FAST_TRACK = 'FAST_TRACK',
  AWAITING_CONFIRMATION = 'AWAITING_CONFIRMATION',
  DISPATCHING = 'DISPATCHING',
  SENT_VIA_PERSONAL = 'SENT_VIA_PERSONAL',
  SENT_VIA_BOT = 'SENT_VIA_BOT',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
  EXPIRED = 'EXPIRED'
}

export type DispatchMode = 'HYBRID' | 'PERSONAL_ONLY' | 'BOT_ONLY';

/** Maximum UTF-8 character length enforced in Phase 1 (plain-text only, BR-02). */
export const MAX_PLAINTEXT_MESSAGE_LENGTH = 500;

export interface ScheduledMessagePayload {
  /** Plain-text UTF-8 body (<= 500 characters; multimedia prohibited in v4.4). */
  text: string;
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
  idempotencyKey: string;
  retryCount: number;
  status?: ScheduledMessageStatus;
  dispatchMode?: DispatchMode;
  autoFallback?: boolean;
  version?: number;
  templateName?: string;
  templateLanguage?: string;
  waMeLink?: string;
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
