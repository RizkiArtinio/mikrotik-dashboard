import { apiClient } from "./apiClient";
import type { BackupItem } from "@/types/backup";

export const backupApi = {
  list: async (routerId: number): Promise<BackupItem[]> =>
    (await apiClient.get<BackupItem[]>(`/routers/${routerId}/backups`)).data,
  trigger: async (routerId: number): Promise<BackupItem[]> =>
    (await apiClient.post<BackupItem[]>(`/routers/${routerId}/backups`)).data,
  // Downloads require the JWT bearer header, so this goes through axios
  // (with its auth interceptor) rather than a plain <a href> navigation.
  download: async (backupId: number, fileName: string): Promise<void> => {
    const response = await apiClient.get(`/backups/${backupId}/download`, { responseType: "blob" });
    const url = URL.createObjectURL(response.data as Blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(url);
  },
};
