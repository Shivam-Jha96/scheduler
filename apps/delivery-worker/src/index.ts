import { initializeAdapters } from './registry.js';
import { Logger } from '@scheduler/logger';

const logger = new Logger('WorkerBootstrap');

async function main() {
  logger.info('Initializing Model C v4.4 HYBRID transport adapters...');
  initializeAdapters();
  logger.info('Delivery Worker pool ready for PostgreSQL 16+ CAS lease dispatch.');
}

main();
