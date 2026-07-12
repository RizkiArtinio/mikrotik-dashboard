export type AlertType = "router_down" | "vpn_down" | "cpu_high" | "mem_high" | "isp_down";

export interface AlertRule {
  id: number;
  alert_type: AlertType;
  threshold_value: number | null;
  cooldown_minutes: number;
  is_enabled: boolean;
  notify_telegram: boolean;
  notify_email: boolean;
  description: string | null;
}

export interface AlertRuleUpdatePayload {
  threshold_value?: number;
  cooldown_minutes?: number;
  is_enabled?: boolean;
  notify_telegram?: boolean;
  notify_email?: boolean;
}

export interface NotificationLogEntry {
  id: number;
  router_id: number | null;
  alert_type: string;
  target_identifier: string | null;
  message: string;
  channel: string;
  resolved: boolean;
  sent_at: string;
}
