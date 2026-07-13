import { apiClient } from "./apiClient";
import type {
  L2tpPeerCreatePayload,
  L2tpPeerResult,
  VpnPeer,
  WireguardPeerCreatePayload,
  WireguardPeerResult,
} from "@/types/vpn";

export const vpnApi = {
  list: async (routerId: number): Promise<VpnPeer[]> =>
    (await apiClient.get<VpnPeer[]>(`/routers/${routerId}/vpn`)).data,
  createWireguardPeer: async (
    routerId: number,
    payload: WireguardPeerCreatePayload,
  ): Promise<WireguardPeerResult> =>
    (await apiClient.post<WireguardPeerResult>(`/routers/${routerId}/vpn/wireguard-peer`, payload)).data,
  createL2tpPeer: async (routerId: number, payload: L2tpPeerCreatePayload): Promise<L2tpPeerResult> =>
    (await apiClient.post<L2tpPeerResult>(`/routers/${routerId}/vpn/l2tp-peer`, payload)).data,
};
