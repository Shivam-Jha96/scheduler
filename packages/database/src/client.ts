// Database client wrapper
export interface DatabaseConfig {
  url?: string;
}

export class DatabaseService {
  private static instance: DatabaseService;
  private connected: boolean = false;

  private constructor() {}

  public static getInstance(): DatabaseService {
    if (!DatabaseService.instance) {
      DatabaseService.instance = new DatabaseService();
    }
    return DatabaseService.instance;
  }

  public async connect(): Promise<void> {
    this.connected = true;
  }

  public async disconnect(): Promise<void> {
    this.connected = false;
  }

  public isConnected(): boolean {
    return this.connected;
  }
}

export const dbService = DatabaseService.getInstance();
