import { apiClient } from "./apiClient";
import type { ConnectionTestResult, RouterCreatePayload, RouterItem, RouterUpdatePayload } from "@/types/router";

export const routerApi = {
  list: async (): Promise<RouterItem[]> => (await apiClient.get<RouterItem[]>("/routers")).data,
  get: async (id: number): Promise<RouterItem> => (await apiClient.get<RouterItem>(`/routers/${id}`)).data,
  create: async (payload: RouterCreatePayload): Promise<RouterItem> =>
    (await apiClient.post<RouterItem>("/routers", payload)).data,
  update: async (id: number, payload: RouterUpdatePayload): Promise<RouterItem> =>
    (await apiClient.put<RouterItem>(`/routers/${id}`, payload)).data,
  remove: async (id: number): Promise<void> => {
    await apiClient.delete(`/routers/${id}`);
  },
  testConnection: async (id: number): Promise<ConnectionTestResult> =>
    (await apiClient.post<ConnectionTestResult>(`/routers/${id}/test-connection`)).data,
};
