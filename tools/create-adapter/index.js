#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
function getArg(flag, defaultValue) {
  const idx = args.indexOf(flag);
  if (idx !== -1 && args[idx + 1]) {
    return args[idx + 1];
  }
  return defaultValue;
}

const name = getArg('--name');
const display = getArg('--display', name ? name.toUpperCase() : 'Custom Channel');

if (!name) {
  console.error('Error: --name argument is required.');
  console.log('Usage: node tools/create-adapter/index.js --name <channel-slug> [--display "Display Name"]');
  process.exit(1);
}

const targetDir = path.resolve(__dirname, '../../adapters', name);
if (fs.existsSync(targetDir)) {
  console.error(`Error: Adapter "${name}" already exists at ${targetDir}`);
  process.exit(1);
}

fs.mkdirSync(path.join(targetDir, 'src'), { recursive: true });
fs.mkdirSync(path.join(targetDir, 'test'), { recursive: true });

// 1. package.json
const pkgJson = {
  name: `@scheduler/adapter-${name}`,
  version: '1.0.0',
  description: `${display} adapter for Omnichannel Message Scheduler`,
  main: './dist/index.js',
  types: './dist/index.d.ts',
  scripts: {
    build: 'tsc -b',
    typecheck: 'tsc --noEmit',
    test: 'node --test',
    clean: 'rm -rf dist'
  },
  dependencies: {
    '@scheduler/adapter-sdk': '*',
    '@scheduler/types': '*'
  },
  devDependencies: {
    '@scheduler/typescript-config': '*',
    'typescript': '^5.7.3'
  }
};
fs.writeFileSync(path.join(targetDir, 'package.json'), JSON.stringify(pkgJson, null, 2));

// 2. tsconfig.json
const tsconfig = {
  extends: '@scheduler/typescript-config/node.json',
  include: ['src/**/*'],
  compilerOptions: {
    outDir: 'dist',
    rootDir: 'src'
  }
};
fs.writeFileSync(path.join(targetDir, 'tsconfig.json'), JSON.stringify(tsconfig, null, 2));

// 3. Adapter Implementation
const pascalName = name.replace(/(^|-)([a-z])/g, (_, __, letter) => letter.toUpperCase());
const adapterCode = `import { 
  IChannelAdapter, 
  ChannelCapabilities, 
  ChannelAccountConfig, 
  HealthStatus, 
  RecipientValidationResult, 
  DeliveryReceipt, 
  ScheduledMessageJob 
} from '@scheduler/adapter-sdk';

export class ${pascalName}Adapter implements IChannelAdapter {
  readonly channelId = '${name}';
  readonly displayName = '${display}';

  readonly capabilities: ChannelCapabilities = {
    supportsRichText: true,
    supportsMarkdown: true,
    supportsMedia: ['IMAGE', 'DOCUMENT'],
    supportsButtons: false,
    supportsReactions: false,
    supportsDeliveryReceipts: true,
    requiresPersistentSession: false,
    maxPayloadLength: 4096,
    rateLimit: {
      maxPerMinute: 60,
      burst: 10,
      recommendedJitterMs: 500
    }
  };

  async initialize(accountConfig: ChannelAccountConfig): Promise<void> {
    // TODO: Initialize connection, authenticate client, verify tokens
  }

  async shutdown(accountId: string): Promise<void> {
    // TODO: Gracefully close connection
  }

  async checkHealth(accountId: string): Promise<HealthStatus> {
    return {
      channelId: this.channelId,
      accountId,
      healthy: true,
      latencyMs: 10,
      timestamp: new Date()
    };
  }

  async validateRecipient(accountId: string, recipientId: string): Promise<RecipientValidationResult> {
    // Basic validation format check
    return {
      isValid: recipientId.trim().length > 0,
      formattedId: recipientId.trim()
    };
  }

  async sendMessage(job: ScheduledMessageJob): Promise<DeliveryReceipt> {
    // TODO: Dispatch message via ${display} API or socket
    return {
      messageId: job.id,
      externalMessageId: \`${name}-\${Date.now()}\`,
      channelId: this.channelId,
      recipientId: job.recipientId,
      status: 'DELIVERED',
      deliveredAt: new Date()
    };
  }
}
`;
fs.writeFileSync(path.join(targetDir, 'src', `${name}.adapter.ts`), adapterCode);

// 4. Index export
const indexCode = `export * from './${name}.adapter.js';\n`;
fs.writeFileSync(path.join(targetDir, 'src', 'index.ts'), indexCode);

console.log(`Successfully scaffolded new adapter "@scheduler/adapter-${name}" at adapters/${name}`);
