import { apiClient } from "./apiClient";
import type { IspStatusResponse } from "@/types/misc";

export const ispApi = {
  status: async (routerId: number): Promise<IspStatusResponse> =>
    (await apiClient.get<IspStatusResponse>(`/routers/${routerId}/isp-status`)).data,
};
