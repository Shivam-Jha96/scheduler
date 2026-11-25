import { z } from 'zod';

/**
 * Canonical Model C v4.4 HYBRID Environment Configuration Schema.
 * Phase 1 runs purely on PostgreSQL 16+ (pg_cron + CAS leases) with zero Redis/BullMQ dependencies.
 */
export const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),

  // PostgreSQL 16+ (pg_cron >= 1.5, pgcrypto, uuid-ossp)
  DATABASE_URL: z
    .string()
    .min(1)
    .default('postgresql://scheduler:scheduler_secret@localhost:5432/scheduler_db'),

  // Cloud KMS Envelope Encryption & High-Entropy Blind Indexing (EPIC-13)
  KMS_KEY_ID: z.string().min(1).default('alias/schedulerbot-dek'),
  KMS_ENDPOINT_URL: z.string().url().optional(),
  PHONE_PEPPER: z
    .string()
    .min(32)
    .default('dev-phone-pepper-replace-with-64-hex-kms-managed-secret-00000000'),
  APP_DEK_CIPHERTEXT: z.string().optional(),
  APP_DEK_MAP: z.string().optional(),

  // Ingress Fastify Gateway
  PORT: z.coerce.number().int().positive().default(3000),
  HOST: z.string().default('0.0.0.0'),

  // Meta WhatsApp Business Cloud API v22.0 (EPIC-07)
  META_GRAPH_API_BASE_URL: z.string().url().default('https://graph.facebook.com'),
  META_GRAPH_API_VERSION: z.string().default('v22.0'),
  META_APP_SECRET: z.string().min(1).default('dev-meta-app-secret'),
  META_VERIFY_TOKEN: z.string().min(1).default('mock_verify_token_12345'),
  WABA_PHONE_NUMBER_ID: z.string().min(1).default('15551234567'),
  META_SYSTEM_USER_TOKEN: z.string().min(1).default('dev-system-user-token'),

  // Volatile-RAM NLU Schedule Parsing Service (EPIC-02)
  NLU_ENDPOINT_URL: z.string().url().default('http://localhost:8080/v1/parse-schedule'),

  // Local / CI MockAPI_Server override (M0-T3)
  MOCK_API_BASE_URL: z.string().url().optional()
});

export type AppConfig = z.infer<typeof envSchema>;

export function loadConfig(env = process.env): AppConfig {
  const result = envSchema.safeParse(env);
  if (!result.success) {
    console.error('Invalid environment variables:', result.error.format());
    throw new Error('Environment configuration validation failed');
  }
  return result.data;
}
