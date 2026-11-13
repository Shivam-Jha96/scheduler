import Fastify from 'fastify';
import { loadConfig } from '@scheduler/config';
import { Logger } from '@scheduler/logger';
import { adapterRegistry } from '@scheduler/adapter-registry';

const logger = new Logger('APIGateway');

export async function createServer() {
  const config = loadConfig();
  const fastify = Fastify({ logger: false });

  // Health check endpoint
  fastify.get('/health', async () => {
    return {
      status: 'ok',
      service: 'api-gateway',
      adapters: adapterRegistry.list(),
      timestamp: new Date().toISOString()
    };
  });

  // Dynamic Inbound Webhook Router for any channel
  fastify.post('/api/webhooks/:channelId', async (request, reply) => {
    const { channelId } = request.params as { channelId: string };
    logger.info(`Received inbound webhook for channel: ${channelId}`);

    if (!adapterRegistry.has(channelId)) {
      reply.status(404);
      return { error: `Channel adapter not registered: ${channelId}` };
    }

    const adapter = adapterRegistry.get(channelId);
    if (!adapter.handleWebhook) {
      return { status: 'acknowledged', message: 'Adapter has no custom webhook handler' };
    }

    const headers = Object.fromEntries(
      Object.entries(request.headers).map(([k, v]) => [k, Array.isArray(v) ? v.join(',') : v || ''])
    );

    const result = await adapter.handleWebhook(request.body, headers);
    return { status: 'success', result };
  });

  // Schedule creation REST endpoint
  fastify.post('/api/schedules', async (request, reply) => {
    // In production: validates schedule payload, creates DB record, assigns idempotency key
    return {
      status: 'accepted',
      scheduleId: `sched-${Date.now()}`,
      message: 'Message scheduled successfully'
    };
  });

  return { fastify, config };
}
