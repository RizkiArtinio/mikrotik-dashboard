import type { InterfaceItem } from "./interface";
import type { VpnPeer } from "./vpn";

export interface ResourceSnapshot {
  cpu_load: number | null;
  free_memory: number | null;
  total_memory: number | null;
  memory_usage_percent: number | null;
  free_hdd_space: number | null;
  total_hdd_space: number | null;
  disk_usage_percent: number | null;
  uptime: string | null;
  version: string | null;
  board_name: string | null;
  cpu_count: number | null;
  architecture_name: string | null;
}

export interface HealthSnapshot {
  voltage: number | null;
  temperature: number | null;
  cpu_temperature: number | null;
}

export interface DashboardSnapshot {
  router_id: number;
  router_name: string;
  online: boolean;
  uptime: string | null;
  resources: ResourceSnapshot | null;
  health: HealthSnapshot | null;
  total_rx_bps: number;
  total_tx_bps: number;
  active_vpn_count: number;
  active_user_count: number;
  interfaces: InterfaceItem[];
  vpn_peers: VpnPeer[];
  generated_at: string;
  error: string | null;
}
