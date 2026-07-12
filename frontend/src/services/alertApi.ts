import { apiClient } from "./apiClient";
import type { AlertRule, AlertRuleUpdatePayload, NotificationLogEntry } from "@/types/alert";

export const alertApi = {
  listRules: async (): Promise<AlertRule[]> => (await apiClient.get<AlertRule[]>("/alert-rules")).data,
  updateRule: async (id: number, payload: AlertRuleUpdatePayload): Promise<AlertRule> =>
    (await apiClient.put<AlertRule>(`/alert-rules/${id}`, payload)).data,
  notificationLog: async (limit = 100): Promise<NotificationLogEntry[]> =>
    (await apiClient.get<NotificationLogEntry[]>("/notification-log", { params: { limit } })).data,
};
