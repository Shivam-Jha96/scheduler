import { IChannelAdapter } from '@scheduler/adapter-sdk';

export class AdapterRegistry {
  private static instance: AdapterRegistry;
  private adapters = new Map<string, IChannelAdapter>();

  private constructor() {}

  public static getInstance(): AdapterRegistry {
    if (!AdapterRegistry.instance) {
      AdapterRegistry.instance = new AdapterRegistry();
    }
    return AdapterRegistry.instance;
  }

  public register(adapter: IChannelAdapter): void {
    if (this.adapters.has(adapter.channelId)) {
      console.warn(`[AdapterRegistry] Overriding existing adapter for channel: ${adapter.channelId}`);
    }
    this.adapters.set(adapter.channelId, adapter);
  }

  public get(channelId: string): IChannelAdapter {
    const adapter = this.adapters.get(channelId);
    if (!adapter) {
      throw new Error(`[AdapterRegistry] No adapter registered for channel: "${channelId}". Available channels: ${Array.from(this.adapters.keys()).join(', ')}`);
    }
    return adapter;
  }

  public has(channelId: string): boolean {
    return this.adapters.has(channelId);
  }

  public list(): { channelId: string; displayName: string }[] {
    return Array.from(this.adapters.values()).map(a => ({
      channelId: a.channelId,
      displayName: a.displayName
    }));
  }
}

export const adapterRegistry = AdapterRegistry.getInstance();
