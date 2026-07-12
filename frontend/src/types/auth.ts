export type UserRole = "super_admin" | "network_engineer" | "viewer";

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: UserRole;
  email: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}
