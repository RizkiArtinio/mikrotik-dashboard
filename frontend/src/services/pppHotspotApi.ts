import { apiClient } from "./apiClient";
import type { HotspotUser, PppUser } from "@/types/misc";

export const pppHotspotApi = {
  pppUsers: async (routerId: number): Promise<PppUser[]> =>
    (await apiClient.get<{ users: PppUser[] }>(`/routers/${routerId}/ppp-users`)).data.users,
  hotspotUsers: async (routerId: number): Promise<HotspotUser[]> =>
    (await apiClient.get<{ users: HotspotUser[] }>(`/routers/${routerId}/hotspot-users`)).data.users,
};
