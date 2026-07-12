import { apiClient } from "./apiClient";
import type { DashboardSnapshot } from "@/types/dashboard";

export const dashboardApi = {
  get: async (routerId: number): Promise<DashboardSnapshot> =>
    (await apiClient.get<DashboardSnapshot>(`/routers/${routerId}/dashboard`)).data,
};
