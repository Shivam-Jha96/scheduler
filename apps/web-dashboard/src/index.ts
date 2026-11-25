// Phase 2 (M7 / EPIC-11) Next.js / React management dashboard placeholder.
// Quarantined outside Phase 1 v4.4 HYBRID WhatsApp-native MVP runtime.
export interface DashboardStats {
  totalScheduled: number;
  totalDelivered: number;
  activeChannels: string[];
}

export function getInitialDashboardStats(): DashboardStats {
  return {
    totalScheduled: 0,
    totalDelivered: 0,
    activeChannels: ['whatsapp-cloud-api']
  };
}
