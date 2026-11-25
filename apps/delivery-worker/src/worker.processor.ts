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

    // Execute delivery directly through the official transport adapter port
    // (v1.2 typing simulation / jitter heuristics permanently retired in Model C v4.4)
    const receipt = await adapter.sendMessage(job);
    logger.info(`Message dispatched successfully: ${job.id}`, { receipt });

    return receipt;
  }
}

export const workerProcessor = new DeliveryWorkerProcessor();
