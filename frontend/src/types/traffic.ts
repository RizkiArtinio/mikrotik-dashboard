export type BandwidthRange = "day" | "week" | "month";

export interface TrafficHistoryPoint {
  timestamp: string;
  rx: number;
  tx: number;
}

export interface BandwidthHistoryResponse {
  router_id: number;
  interface_name: string;
  range: BandwidthRange;
  points: TrafficHistoryPoint[];
}
