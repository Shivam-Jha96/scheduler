#!/usr/bin/env node
/**
 * M0-T4 / EP12-G2 Guardrail Checker
 * Fails CI if retired v1.2 dependencies, retired directories, invalid SQL casts,
 * or forbidden low-entropy name hash columns re-enter the repository.
 */
import fs from 'node:fs';
import path from 'node:path';

const ROOT = process.cwd();
const errors = [];

const FORBIDDEN_PACKAGES = [
  '@whiskeysockets/baileys',
  'bullmq',
  'pg-boss',
  'redlock',
  '@aws-sdk/client-s3',
  '@prisma/client',
  'prisma'
];

const FORBIDDEN_DIRECTORIES = [
  'adapters/whatsapp-baileys',
  'apps/scheduler-feeder',
  'packages/queue',
  'packages/database/prisma'
];

function walk(dir, filterFn, results = []) {
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === 'node_modules' || entry.name === 'dist' || entry.name === '.git' || entry.name === '.turbo') {
      continue;
    }
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, filterFn, results);
    } else if (filterFn(full)) {
      results.push(full);
    }
  }
  return results;
}

// 1. Retired directories check
for (const rel of FORBIDDEN_DIRECTORIES) {
  if (fs.existsSync(path.join(ROOT, rel))) {
    errors.push(`Retired v1.2 directory still exists: ${rel}`);
  }
}

// 2. Forbidden dependencies across all package.json files
const pkgFiles = walk(ROOT, (f) => path.basename(f) === 'package.json');
for (const file of pkgFiles) {
  const pkg = JSON.parse(fs.readFileSync(file, 'utf8'));
  const allDeps = {
    ...(pkg.dependencies || {}),
    ...(pkg.devDependencies || {}),
    ...(pkg.optionalDependencies || {})
  };
  for (const banned of FORBIDDEN_PACKAGES) {
    if (Object.prototype.hasOwnProperty.call(allDeps, banned)) {
      errors.push(`Forbidden v1.2 dependency "${banned}" found in ${path.relative(ROOT, file)}`);
    }
  }
  if (pkg.scripts?.clean && pkg.scripts.clean.includes('rm -rf')) {
    errors.push(`POSIX-only "rm -rf" clean script found in ${path.relative(ROOT, file)}`);
  }
}

// 3. Forbidden source patterns (R2 bucket URL, Baileys, invalid SQL cast, name hashes)
const codeFiles = walk(ROOT, (f) => /\.(ts|tsx|js|mjs|cjs|sql)$/.test(f) && !f.endsWith('check-v12-guardrails.mjs'));
for (const file of codeFiles) {
  const rel = path.relative(ROOT, file).replace(/\\/g, '/');
  if (rel.startsWith('tests/') || rel.startsWith('docs/') || rel.startsWith('conversations/')) continue;
  const content = fs.readFileSync(file, 'utf8');

  if (content.includes('r2.cloudflarestorage.com')) {
    errors.push(`Forbidden R2 multimedia reference found in ${rel}`);
  }
  if (content.includes('@whiskeysockets/baileys') || content.includes('@scheduler/adapter-whatsapp-baileys')) {
    errors.push(`Forbidden Baileys import/reference found in ${rel}`);
  }
  if (content.includes("'\\E'\\\\x00'::bytea'::bytea")) {
    errors.push(`Invalid duplicated SQL bytea cast (Erratum A.2 #2) found in ${rel}`);
  }
  if (rel.endsWith('.sql') && /\b(sender_name_hash|recipient_name_hash)\b/.test(content)) {
    errors.push(`Forbidden low-entropy name hash column found in SQL file ${rel}`);
  }
}

if (errors.length > 0) {
  console.error('M0-T4 / EP12-G2 Guardrail Check FAILED:');
  for (const err of errors) {
    console.error(`  - ${err}`);
  }
  process.exit(1);
}

console.log(`M0-T4 / EP12-G2 Guardrail Check PASSED (${pkgFiles.length} package.json & ${codeFiles.length} code/SQL files scanned).`);
