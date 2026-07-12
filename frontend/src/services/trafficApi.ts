import { apiClient } from "./apiClient";
import type { BandwidthHistoryResponse, BandwidthRange } from "@/types/traffic";

export const trafficApi = {
  getHistory: async (
    routerId: number,
    interfaceName: string,
    range: BandwidthRange,
  ): Promise<BandwidthHistoryResponse> =>
    (
      await apiClient.get<BandwidthHistoryResponse>(`/routers/${routerId}/traffic-history`, {
        params: { interface: interfaceName, range },
      })
    ).data,
};
