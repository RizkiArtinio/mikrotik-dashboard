import { apiClient } from "./apiClient";
import type { VpnPeer, WireguardPeerCreatePayload, WireguardPeerResult } from "@/types/vpn";

export const vpnApi = {
  list: async (routerId: number): Promise<VpnPeer[]> =>
    (await apiClient.get<VpnPeer[]>(`/routers/${routerId}/vpn`)).data,
  createWireguardPeer: async (
    routerId: number,
    payload: WireguardPeerCreatePayload,
  ): Promise<WireguardPeerResult> =>
    (await apiClient.post<WireguardPeerResult>(`/routers/${routerId}/vpn/wireguard-peer`, payload)).data,
};
