export interface LogContext {
  correlationId?: string;
  jobId?: string;
  channelId?: string;
  userId?: string;
  [key: string]: unknown;
}

export class Logger {
  constructor(private context: string = 'App') {}

  private redact(obj: unknown): unknown {
    if (!obj || typeof obj !== 'object') return obj;
    const copy = { ...(obj as Record<string, unknown>) };
    const piiKeys = ['password', 'secret', 'token', 'text', 'payload', 'auth', 'credentials'];
    for (const k of Object.keys(copy)) {
      if (piiKeys.some(p => k.toLowerCase().includes(p))) {
        copy[k] = '[REDACTED]';
      }
    }
    return copy;
  }

  public info(msg: string, meta?: LogContext): void {
    console.log(JSON.stringify({
      level: 'info',
      context: this.context,
      message: msg,
      meta: this.redact(meta),
      timestamp: new Date().toISOString()
    }));
  }

  public error(msg: string, error?: unknown, meta?: LogContext): void {
    console.error(JSON.stringify({
      level: 'error',
      context: this.context,
      message: msg,
      error: error instanceof Error ? { message: error.message, stack: error.stack } : error,
      meta: this.redact(meta),
      timestamp: new Date().toISOString()
    }));
  }

  public debug(msg: string, meta?: LogContext): void {
    if (process.env.LOG_LEVEL === 'debug') {
      console.debug(JSON.stringify({
        level: 'debug',
        context: this.context,
        message: msg,
        meta: this.redact(meta),
        timestamp: new Date().toISOString()
      }));
    }
  }
}

export const logger = new Logger('Global');
