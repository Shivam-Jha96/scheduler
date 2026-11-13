// Next.js / React management dashboard entrypoint
export interface DashboardStats {
  totalScheduled: number;
  totalDelivered: number;
  activeChannels: string[];
}

export function getInitialDashboardStats(): DashboardStats {
  return {
    totalScheduled: 0,
    totalDelivered: 0,
    activeChannels: ['whatsapp-baileys', 'telegram', 'discord', 'slack', 'webhook']
  };
}
