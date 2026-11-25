import { adapterRegistry } from '@scheduler/adapter-registry';
import { whatsAppCloudApiAdapter } from '@scheduler/adapter-whatsapp-cloud-api';

/**
 * Registers Phase 1 v4.4 HYBRID production transports only.
 * Phase 2 omnichannel adapters (Viber, Discord, Signal, LINE, iMessage) are
 * quarantined until M6/M7 (EPIC-08..10). V1.2 Baileys is permanently retired.
 */
export function initializeAdapters(): void {
  adapterRegistry.register(whatsAppCloudApiAdapter);
}
