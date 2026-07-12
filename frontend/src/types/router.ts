export interface RouterItem {
  id: number;
  name: string;
  ip_address: string;
  username: string;
  api_port: number;
  use_ssl: boolean;
  site: string | null;
  isp_gateway: string | null;
  wireguard_endpoint: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface RouterCreatePayload {
  name: string;
  ip_address: string;
  username: string;
  password: string;
  api_port?: number;
  use_ssl?: boolean;
  site?: string;
  isp_gateway?: string;
  wireguard_endpoint?: string;
}

export type RouterUpdatePayload = Partial<RouterCreatePayload> & { is_active?: boolean };

export interface ConnectionTestResult {
  success: boolean;
  message: string;
  identity: string | null;
  routeros_version: string | null;
}
