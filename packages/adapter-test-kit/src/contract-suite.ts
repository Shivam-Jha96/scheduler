import { IChannelAdapter, ScheduledMessageJob } from '@scheduler/adapter-sdk';

export interface AdapterTestOptions {
  mockRecipient: string;
  mockAccountConfig: {
    accountId: string;
    userId: string;
    channelId: string;
    accountIdentifier: string;
    credentials: Record<string, unknown>;
  };
}

export async function runAdapterContractSuite(adapter: IChannelAdapter, options: AdapterTestOptions): Promise<void> {
  console.log(`[ContractSuite] Testing adapter contract: ${adapter.displayName} (${adapter.channelId})`);

  // 1. Verify channel identity
  if (!adapter.channelId || typeof adapter.channelId !== 'string') {
    throw new Error('Contract Failure: adapter.channelId must be a non-empty string');
  }

  // 2. Verify capabilities structure
  const caps = adapter.capabilities;
  if (!caps || typeof caps.supportsRichText !== 'boolean' || !Array.isArray(caps.supportsMedia)) {
    throw new Error('Contract Failure: adapter.capabilities missing standard shape');
  }

  // 3. Test initialization
  await adapter.initialize(options.mockAccountConfig);

  // 4. Test health probe
  const health = await adapter.checkHealth(options.mockAccountConfig.accountId);
  if (typeof health.healthy !== 'boolean') {
    throw new Error('Contract Failure: checkHealth must return a boolean healthy field');
  }

  // 5. Test recipient validation
  const validation = await adapter.validateRecipient(options.mockAccountConfig.accountId, options.mockRecipient);
  if (typeof validation.isValid !== 'boolean') {
    throw new Error('Contract Failure: validateRecipient must return a boolean isValid');
  }

  // 6. Test send message dispatch
  const mockJob: ScheduledMessageJob = {
    id: 'test-job-uuid-1234',
    userId: options.mockAccountConfig.userId,
    channelAccountId: options.mockAccountConfig.accountId,
    channelId: adapter.channelId,
    recipientId: options.mockRecipient,
    payload: {
      text: 'Automated contract verification test message'
    },
    scheduledFor: new Date(),
    timezone: 'UTC',
    idempotencyKey: 'idemp-test-1234',
    retryCount: 0
  };

  const receipt = await adapter.sendMessage(mockJob);
  if (!receipt || !receipt.status || receipt.channelId !== adapter.channelId) {
    throw new Error('Contract Failure: sendMessage must return a valid DeliveryReceipt matching the channelId');
  }

  console.log(`[ContractSuite] PASSED for ${adapter.displayName}`);
}
