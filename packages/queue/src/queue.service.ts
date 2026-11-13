import { ScheduledMessageJob } from '@scheduler/types';

export interface QueueConfig {
  redisHost: string;
  redisPort: number;
  redisPassword?: string;
  queueName?: string;
}

export class QueueService {
  private static instance: QueueService;
  private queueName: string;

  private constructor(config?: Partial<QueueConfig>) {
    this.queueName = config?.queueName || 'scheduled-messages';
  }

  public static getInstance(config?: Partial<QueueConfig>): QueueService {
    if (!QueueService.instance) {
      QueueService.instance = new QueueService(config);
    }
    return QueueService.instance;
  }

  public async stageJob(job: ScheduledMessageJob, delayMs: number): Promise<string> {
    // In production BullMQ: await this.queue.add('dispatch-message', job, { delay: delayMs, jobId: job.id });
    return job.id;
  }

  public async cancelJob(jobId: string): Promise<boolean> {
    return true;
  }
}

export const queueService = QueueService.getInstance();
