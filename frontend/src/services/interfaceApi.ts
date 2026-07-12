import { apiClient } from "./apiClient";
import type { InterfaceItem } from "@/types/interface";

export const interfaceApi = {
  list: async (routerId: number): Promise<InterfaceItem[]> =>
    (await apiClient.get<InterfaceItem[]>(`/routers/${routerId}/interfaces`)).data,
};
