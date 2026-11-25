export interface RateLimitPolicy {
  maxPerMinute: number;
  burst: number;
  /** Phase 1 official Cloud API requires 0 artificial jitter (v1.2 Baileys heuristics retired). */
  recommendedJitterMs: number;
}

export interface ChannelCapabilities {
  supportsRichText: boolean;
  supportsMarkdown: boolean;
  /** Must be empty (`[]`) in Phase 1 v4.4 (plain-text UTF-8 <= 500 chars only). */
  supportsMedia: readonly string[];
  supportsButtons: boolean;
  supportsReactions: boolean;
  supportsDeliveryReceipts: boolean;
  requiresPersistentSession: boolean;
  maxPayloadLength: number;
  rateLimit: RateLimitPolicy;
}
