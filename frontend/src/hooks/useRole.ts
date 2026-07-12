import { useAuth } from "./useAuth";

export function useRole() {
  const { user, hasRole } = useAuth();
  return {
    role: user?.role ?? null,
    isSuperAdmin: hasRole("super_admin"),
    isEngineerOrAdmin: hasRole("super_admin", "network_engineer"),
    hasRole,
  };
}
