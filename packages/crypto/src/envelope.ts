import crypto from 'node:crypto';

export interface EncryptedEnvelope {
  encryptedPayload: Buffer;
  iv: Buffer;
  authTag: Buffer;
  keyFingerprint: string;
}

export class EnvelopeEncryption {
  private static readonly ALGORITHM = 'aes-256-gcm';
  private static readonly IV_LENGTH = 12; // 96 bits for GCM

  public static encrypt(plainText: string, masterKeyHex: string, fingerprint = 'v1'): EncryptedEnvelope {
    const key = Buffer.from(masterKeyHex, 'hex');
    const iv = crypto.randomBytes(this.IV_LENGTH);
    const cipher = crypto.createCipheriv(this.ALGORITHM, key, iv);

    const encrypted = Buffer.concat([cipher.update(plainText, 'utf8'), cipher.final()]);
    const authTag = cipher.getAuthTag();

    return {
      encryptedPayload: encrypted,
      iv,
      authTag,
      keyFingerprint: fingerprint
    };
  }

  public static decrypt(envelope: EncryptedEnvelope, masterKeyHex: string): string {
    const key = Buffer.from(masterKeyHex, 'hex');
    const decipher = crypto.createDecipheriv(this.ALGORITHM, key, envelope.iv);
    decipher.setAuthTag(envelope.authTag);

    const decrypted = Buffer.concat([decipher.update(envelope.encryptedPayload), decipher.final()]);
    return decrypted.toString('utf8');
  }

  public static generateIdempotencyKey(userId: string, recipientId: string, timestampMs: number, payloadText: string): string {
    const hash = crypto.createHash('sha256');
    hash.update(`${userId}:${recipientId}:${timestampMs}:${payloadText}`);
    return hash.digest('hex');
  }
}
