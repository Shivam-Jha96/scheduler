import { adapterRegistry } from '@scheduler/adapter-registry';
import { whatsAppBaileysAdapter } from '@scheduler/adapter-whatsapp-baileys';
import { whatsAppCloudApiAdapter } from '@scheduler/adapter-whatsapp-cloud-api';
import { telegramAdapter } from '@scheduler/adapter-telegram';
import { discordAdapter } from '@scheduler/adapter-discord';
import { slackAdapter } from '@scheduler/adapter-slack';
import { genericWebhookAdapter } from '@scheduler/adapter-webhook';

export function initializeAdapters(): void {
  // Register all pluggable omnichannel transports
  adapterRegistry.register(whatsAppBaileysAdapter);
  adapterRegistry.register(whatsAppCloudApiAdapter);
  adapterRegistry.register(telegramAdapter);
  adapterRegistry.register(discordAdapter);
  adapterRegistry.register(slackAdapter);
  adapterRegistry.register(genericWebhookAdapter);
}
