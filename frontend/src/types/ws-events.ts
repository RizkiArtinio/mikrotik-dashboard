import type { DashboardSnapshot } from "./dashboard";
import type { InterfaceItem } from "./interface";

export interface WsEvent<T> {
  type: string;
  router_id: number;
  data: T;
  ts: string;
}

export type DashboardUpdateEvent = WsEvent<DashboardSnapshot>;
export type InterfaceUpdateEvent = WsEvent<InterfaceItem[]>;
