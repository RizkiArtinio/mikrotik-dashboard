import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { ProtectedRoute } from "@/components/common/ProtectedRoute";
import { RoleGate } from "@/components/common/RoleGate";
import AlertSettingsPage from "@/pages/AlertSettingsPage";
import BackupPage from "@/pages/BackupPage";
import BandwidthPage from "@/pages/BandwidthPage";
import DashboardPage from "@/pages/DashboardPage";
import DhcpPage from "@/pages/DhcpPage";
import FirewallPage from "@/pages/FirewallPage";
import InterfacesPage from "@/pages/InterfacesPage";
import IspPage from "@/pages/IspPage";
import L2tpGeneratorPage from "@/pages/L2tpGeneratorPage";
import LoginPage from "@/pages/LoginPage";
import OvpnGeneratorPage from "@/pages/OvpnGeneratorPage";
import RouterAdminPage from "@/pages/RouterAdminPage";
import UserAdminPage from "@/pages/UserAdminPage";
import UsersActivityPage from "@/pages/UsersActivityPage";
import VpnGeneratorPage from "@/pages/VpnGeneratorPage";
import VpnPage from "@/pages/VpnPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppShell>
              <Routes>
                <Route index element={<DashboardPage />} />
                <Route path="interfaces" element={<InterfacesPage />} />
                <Route path="bandwidth" element={<BandwidthPage />} />
                <Route path="vpn" element={<VpnPage />} />
                <Route
                  path="vpn/generate"
                  element={
                    <RoleGate roles={["super_admin", "network_engineer"]}>
                      <VpnGeneratorPage />
                    </RoleGate>
                  }
                />
                <Route
                  path="vpn/generate-l2tp"
                  element={
                    <RoleGate roles={["super_admin", "network_engineer"]}>
                      <L2tpGeneratorPage />
                    </RoleGate>
                  }
                />
                <Route
                  path="vpn/generate-ovpn"
                  element={
                    <RoleGate roles={["super_admin", "network_engineer"]}>
                      <OvpnGeneratorPage />
                    </RoleGate>
                  }
                />
                <Route path="backup" element={<BackupPage />} />
                <Route path="isp" element={<IspPage />} />
                <Route path="firewall" element={<FirewallPage />} />
                <Route path="dhcp" element={<DhcpPage />} />
                <Route path="users-activity" element={<UsersActivityPage />} />
                <Route
                  path="admin/routers"
                  element={
                    <RoleGate roles={["super_admin"]}>
                      <RouterAdminPage />
                    </RoleGate>
                  }
                />
                <Route
                  path="admin/users"
                  element={
                    <RoleGate roles={["super_admin"]}>
                      <UserAdminPage />
                    </RoleGate>
                  }
                />
                <Route
                  path="admin/alerts"
                  element={
                    <RoleGate roles={["super_admin"]}>
                      <AlertSettingsPage />
                    </RoleGate>
                  }
                />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </AppShell>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}
