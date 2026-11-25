import { Pool, PoolConfig, QueryResult, QueryResultRow } from 'pg';

export interface DatabaseConfig {
  url?: string;
  maxConnections?: number;
  idleTimeoutMillis?: number;
  connectionTimeoutMillis?: number;
}

/**
 * PostgreSQL 16+ connection pool wrapper (`pg`) replacing retired v1.2 Prisma stub.
 * Supports parameterized ACID transactions, atomic CAS leases, and pg_cron reaper queries.
 */
export class DatabaseService {
  private static instance: DatabaseService;
  private pool: Pool | null = null;

  private constructor() {}

  public static getInstance(): DatabaseService {
    if (!DatabaseService.instance) {
      DatabaseService.instance = new DatabaseService();
    }
    return DatabaseService.instance;
  }

  public async connect(config: DatabaseConfig = {}): Promise<void> {
    if (this.pool) return;

    const poolConfig: PoolConfig = {
      connectionString: config.url ?? process.env.DATABASE_URL,
      max: config.maxConnections ?? 20,
      idleTimeoutMillis: config.idleTimeoutMillis ?? 30_000,
      connectionTimeoutMillis: config.connectionTimeoutMillis ?? 5_000
    };

    this.pool = new Pool(poolConfig);
    await this.pool.query('SELECT 1');
  }

  public async query<T extends QueryResultRow = QueryResultRow>(
    text: string,
    params?: unknown[]
  ): Promise<QueryResult<T>> {
    if (!this.pool) {
      throw new Error('DatabaseService is not connected. Call connect() first.');
    }
    return this.pool.query<T>(text, params);
  }

  public getPool(): Pool {
    if (!this.pool) {
      throw new Error('DatabaseService is not connected. Call connect() first.');
    }
    return this.pool;
  }

  public async disconnect(): Promise<void> {
    if (this.pool) {
      await this.pool.end();
      this.pool = null;
    }
  }

  public isConnected(): boolean {
    return this.pool !== null;
  }
}

export const dbService = DatabaseService.getInstance();
