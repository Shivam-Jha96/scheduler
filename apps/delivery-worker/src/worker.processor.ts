import { adapterRegistry } from '@scheduler/adapter-registry';
import { Logger } from '@scheduler/logger';
import { ScheduledMessageJob, DeliveryReceipt } from '@scheduler/types';

const logger = new Logger('DeliveryWorker');

export class DeliveryWorkerProcessor {
  public async processJob(job: ScheduledMessageJob): Promise<DeliveryReceipt> {
    logger.info(`Processing scheduled message job: ${job.id} for channel: ${job.channelId}`, {
      jobId: job.id,
      channelId: job.channelId,
      userId: job.userId
    });

    if (!adapterRegistry.has(job.channelId)) {
      throw new Error(`No adapter found for channel: ${job.channelId}`);
    }

    const adapter = adapterRegistry.get(job.channelId);

    // Optional typing presence
    if (adapter.simulateActivity && adapter.capabilities.rateLimit.recommendedJitterMs > 0) {
      await adapter.simulateActivity(
        job.channelAccountId, 
        job.recipientId, 
        adapter.capabilities.rateLimit.recommendedJitterMs
      );
    }

    // Execute delivery through adapter port
    const receipt = await adapter.sendMessage(job);
    logger.info(`Message delivered successfully: ${job.id}`, { receipt });

    return receipt;
  }
}

export const workerProcessor = new DeliveryWorkerProcessor();
