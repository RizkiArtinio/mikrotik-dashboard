export type BackupType = "backup" | "rsc";
export type BackupTrigger = "manual" | "scheduled";

export interface BackupItem {
  id: number;
  router_id: number;
  file_name: string;
  file_size: number;
  backup_type: BackupType;
  triggered_by: BackupTrigger;
  backup_date: string;
}
