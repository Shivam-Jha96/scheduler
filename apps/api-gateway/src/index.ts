import { createServer } from './server.js';
import { Logger } from '@scheduler/logger';

const logger = new Logger('Bootstrap');

async function main() {
  const { fastify, config } = await createServer();
  try {
    await fastify.listen({ port: config.PORT, host: config.HOST });
    logger.info(`API Gateway listening on http://${config.HOST}:${config.PORT}`);
  } catch (err) {
    logger.error('Failed to start API Gateway', err);
    process.exit(1);
  }
}

main();
