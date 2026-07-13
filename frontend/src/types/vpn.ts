export type VpnType = "wireguard" | "l2tp" | "sstp" | "openvpn" | "ipsec";
export type VpnPeerStatus = "connected" | "disconnected" | "configured" | "unknown";

export interface VpnPeer {
  id: number;
  router_id: number;
  peer_name: string;
  vpn_type: VpnType;
  public_key: string | null;
  allowed_ip: string | null;
  endpoint: string | null;
  dns: string | null;
  description: string | null;
  remote_address: string | null;
  status: VpnPeerStatus;
  rx_bytes: number;
  tx_bytes: number;
  last_seen: string | null;
}

export interface WireguardPeerCreatePayload {
  username: string;
  /** Leave empty to auto-assign the next free IP from Router.wireguard_pool_name. */
  allowed_ip?: string;
  dns: string;
  endpoint?: string;
  description?: string;
}

export interface WireguardPeerResult {
  peer: VpnPeer;
  config_text: string;
  qr_code_base64: string;
}

export interface L2tpPeerCreatePayload {
  /** Leave empty to auto-generate. */
  username?: string;
  /** Leave empty to auto-generate. */
  password?: string;
  description?: string;
}

export interface L2tpPeerResult {
  peer: VpnPeer;
  server_address: string;
  username: string;
  password: string;
  ipsec_psk: string | null;
}
