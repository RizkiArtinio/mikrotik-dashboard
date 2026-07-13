import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { vpnApi } from "@/services/vpnApi";
import type { L2tpPeerCreatePayload, OvpnPeerCreatePayload, WireguardPeerCreatePayload } from "@/types/vpn";

export function useVpnPeers(routerId: number | null) {
  return useQuery({
    queryKey: ["vpn-peers", routerId],
    queryFn: () => vpnApi.list(routerId as number),
    enabled: routerId !== null,
    refetchInterval: 5000,
  });
}

export function useCreateWireguardPeer(routerId: number | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: WireguardPeerCreatePayload) => vpnApi.createWireguardPeer(routerId as number, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vpn-peers", routerId] });
    },
  });
}

export function useCreateL2tpPeer(routerId: number | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: L2tpPeerCreatePayload) => vpnApi.createL2tpPeer(routerId as number, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vpn-peers", routerId] });
    },
  });
}

export function useCreateOvpnPeer(routerId: number | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: OvpnPeerCreatePayload) => vpnApi.createOvpnPeer(routerId as number, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vpn-peers", routerId] });
    },
  });
}
