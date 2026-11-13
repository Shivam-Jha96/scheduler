import { MediaType } from '@scheduler/types';

export interface RateLimitPolicy {
  maxPerMinute: number;
  burst: number;
  recommendedJitterMs: number;
}

export interface ChannelCapabilities {
  supportsRichText: boolean;
  supportsMarkdown: boolean;
  supportsMedia: MediaType[];
  supportsButtons: boolean;
  supportsReactions: boolean;
  supportsDeliveryReceipts: boolean;
  requiresPersistentSession: boolean;
  maxPayloadLength: number;
  rateLimit: RateLimitPolicy;
}
