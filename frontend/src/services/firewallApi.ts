import { apiClient } from "./apiClient";
import type { FirewallStatsResponse, NatStatsResponse } from "@/types/misc";

export const firewallApi = {
  filterStats: async (routerId: number): Promise<FirewallStatsResponse> =>
    (await apiClient.get<FirewallStatsResponse>(`/routers/${routerId}/firewall/filter-stats`)).data,
  natStats: async (routerId: number): Promise<NatStatsResponse> =>
    (await apiClient.get<NatStatsResponse>(`/routers/${routerId}/firewall/nat-stats`)).data,
};
