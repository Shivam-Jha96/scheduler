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
  description: `${display} adapter for SchedulerBot Omnichannel Platform`,
  main: './dist/index.js',
  types: './dist/index.d.ts',
  scripts: {
    build: 'tsc -b',
    typecheck: 'tsc --noEmit',
    test: 'vitest run --passWithNoTests',
    clean: 'node -e "for(const p of [\'dist\',\'tsconfig.tsbuildinfo\'])require(\'fs\').rmSync(p,{recursive:true,force:true})"'
  },
  dependencies: {
    '@scheduler/adapter-sdk': '*',
    '@scheduler/types': '*'
  },
  devDependencies: {
    '@scheduler/typescript-config': '*',
    typescript: '^5.7.3'
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

// 3. Adapter Implementation (Model C v4.4 plain-text defaults: <=500 chars, zero media, zero jitter)
const pascalName = name.replace(/(^|-)([a-z])/g, (_, __, letter) => letter.toUpperCase());
const adapterCode = `import {
  IChannelAdapter,
  ChannelCapabilities,
  ChannelAccountConfig,
  HealthStatus,
  RecipientValidationResult,
  DeliveryReceipt,
  ScheduledMessageJob,
  MAX_PLAINTEXT_MESSAGE_LENGTH
} from '@scheduler/adapter-sdk';

export class ${pascalName}Adapter implements IChannelAdapter {
  readonly channelId = '${name}';
  readonly displayName = '${display}';

  readonly capabilities: ChannelCapabilities = {
    supportsRichText: false,
    supportsMarkdown: false,
    supportsMedia: [],
    supportsButtons: false,
    supportsReactions: false,
    supportsDeliveryReceipts: true,
    requiresPersistentSession: false,
    maxPayloadLength: MAX_PLAINTEXT_MESSAGE_LENGTH,
    rateLimit: {
      maxPerMinute: 60,
      burst: 10,
      recommendedJitterMs: 0
    }
  };

  async initialize(_accountConfig: ChannelAccountConfig): Promise<void> {
    // TODO: Initialize official API client and verify credentials
  }

  async shutdown(_accountId: string): Promise<void> {
    // TODO: Gracefully close client resources
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

  async validateRecipient(_accountId: string, recipientId: string): Promise<RecipientValidationResult> {
    return {
      isValid: recipientId.trim().length > 0,
      formattedId: recipientId.trim()
    };
  }

  async sendMessage(job: ScheduledMessageJob): Promise<DeliveryReceipt> {
    // TODO: Dispatch plain-text message via official ${display} API
    return {
      messageId: job.id,
      externalMessageId: \`${name}-\${Date.now()}\`,
      channelId: this.channelId,
      recipientId: job.recipientId,
      status: 'SENT',
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
