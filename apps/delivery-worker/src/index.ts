import { initializeAdapters } from './registry.js';
import { Logger } from '@scheduler/logger';

const logger = new Logger('WorkerBootstrap');

async function main() {
  logger.info('Initializing omnichannel adapters...');
  initializeAdapters();
  logger.info('Delivery Worker pool ready and awaiting BullMQ jobs.');
}

main();
