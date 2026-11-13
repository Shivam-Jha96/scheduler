import { z } from 'zod';

export const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  DATABASE_URL: z.string().default('postgresql://scheduler:scheduler_secret@localhost:5432/scheduler_db'),
  REDIS_HOST: z.string().default('localhost'),
  REDIS_PORT: z.coerce.number().default(6379),
  REDIS_PASSWORD: z.string().optional(),
  ENCRYPTION_MASTER_KEY: z.string().default('0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'),
  KEY_FINGERPRINT: z.string().default('v1'),
  PORT: z.coerce.number().default(3000),
  HOST: z.string().default('0.0.0.0')
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
