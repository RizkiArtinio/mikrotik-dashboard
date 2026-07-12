export interface FirewallRuleStat {
  chain: string;
  action: string;
  comment: string | null;
  bytes: number;
  packets: number;
  hit_counter: number;
}

export interface FirewallStatsResponse {
  router_id: number;
  rules: FirewallRuleStat[];
}

export interface NatStatsResponse {
  router_id: number;
  rules: FirewallRuleStat[];
}

export interface DhcpLease {
  hostname: string | null;
  mac_address: string;
  ip_address: string;
  status: string | null;
  expires_after: string | null;
}

export interface DhcpLeaseResponse {
  router_id: number;
  leases: DhcpLease[];
}

export interface PppUser {
  username: string;
  service: string | null;
  caller_id: string | null;
  address: string | null;
  login_time: string | null;
  bytes_in: number;
  bytes_out: number;
}

export interface HotspotUser {
  username: string;
  address: string | null;
  mac_address: string | null;
  login_time: string | null;
  bytes_in: number;
  bytes_out: number;
  uptime: string | null;
}

export interface IspPingResult {
  target: string;
  label: string;
  latency_ms: number | null;
  packet_loss_percent: number | null;
  status: "up" | "down";
}

export interface IspStatusResponse {
  router_id: number;
  results: IspPingResult[];
}
