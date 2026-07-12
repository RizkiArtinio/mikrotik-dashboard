import { apiClient } from "./apiClient";
import type { User, UserRole } from "@/types/auth";

export interface UserCreatePayload {
  email: string;
  password: string;
  full_name?: string;
  role: UserRole;
}

export interface UserUpdatePayload {
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
  password?: string;
}

export const userApi = {
  list: async (): Promise<User[]> => (await apiClient.get<User[]>("/users")).data,
  create: async (payload: UserCreatePayload): Promise<User> => (await apiClient.post<User>("/users", payload)).data,
  update: async (id: number, payload: UserUpdatePayload): Promise<User> =>
    (await apiClient.put<User>(`/users/${id}`, payload)).data,
  remove: async (id: number): Promise<void> => {
    await apiClient.delete(`/users/${id}`);
  },
};
