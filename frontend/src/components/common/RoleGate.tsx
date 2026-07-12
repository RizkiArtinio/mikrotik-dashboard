import type { ReactNode } from "react";
import { useRole } from "@/hooks/useRole";
import type { UserRole } from "@/types/auth";

export function RoleGate({ roles, children }: { roles: UserRole[]; children: ReactNode }) {
  const { hasRole } = useRole();
  if (!hasRole(...roles)) return null;
  return <>{children}</>;
}
