import { apiClient } from "./apiClient";
import type { DhcpLeaseResponse } from "@/types/misc";

export const dhcpApi = {
  leases: async (routerId: number): Promise<DhcpLeaseResponse> =>
    (await apiClient.get<DhcpLeaseResponse>(`/routers/${routerId}/dhcp/leases`)).data,
};
