export interface InterfaceItem {
  id: number;
  router_id: number;
  interface_name: string;
  interface_type: string;
  rx_bps: number;
  tx_bps: number;
  rx_bytes: number;
  tx_bytes: number;
  rx_packets: number;
  tx_packets: number;
  status: string;
  updated_at: string;
}
