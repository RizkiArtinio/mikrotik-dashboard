import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import BackupIcon from "@mui/icons-material/Backup";
import DashboardIcon from "@mui/icons-material/Dashboard";
import DnsIcon from "@mui/icons-material/Dns";
import GroupIcon from "@mui/icons-material/Group";
import LanIcon from "@mui/icons-material/Lan";
import NotificationsActiveIcon from "@mui/icons-material/NotificationsActive";
import PublicIcon from "@mui/icons-material/Public";
import RouterIcon from "@mui/icons-material/Router";
import SecurityIcon from "@mui/icons-material/Security";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import VpnKeyIcon from "@mui/icons-material/VpnKey";
import {
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
} from "@mui/material";
import { NavLink } from "react-router-dom";
import { useRole } from "@/hooks/useRole";

const DRAWER_WIDTH = 240;

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: <DashboardIcon /> },
  { to: "/interfaces", label: "Interfaces", icon: <LanIcon /> },
  { to: "/bandwidth", label: "Bandwidth", icon: <ShowChartIcon /> },
  { to: "/vpn", label: "VPN Status", icon: <VpnKeyIcon /> },
  { to: "/vpn/generate", label: "VPN Generator (WireGuard)", icon: <VpnKeyIcon /> },
  { to: "/vpn/generate-l2tp", label: "VPN Generator (L2TP)", icon: <VpnKeyIcon /> },
  { to: "/vpn/generate-ovpn", label: "VPN Generator (OpenVPN)", icon: <VpnKeyIcon /> },
  { to: "/backup", label: "Backup", icon: <BackupIcon /> },
  { to: "/isp", label: "ISP Monitoring", icon: <PublicIcon /> },
  { to: "/firewall", label: "Firewall", icon: <SecurityIcon /> },
  { to: "/dhcp", label: "DHCP Leases", icon: <DnsIcon /> },
  { to: "/users-activity", label: "PPP / Hotspot Users", icon: <GroupIcon /> },
];

const ADMIN_ITEMS = [
  { to: "/admin/routers", label: "Routers", icon: <RouterIcon /> },
  { to: "/admin/users", label: "App Users", icon: <AdminPanelSettingsIcon /> },
  { to: "/admin/alerts", label: "Alert Settings", icon: <NotificationsActiveIcon /> },
];

export function Sidebar() {
  const { isSuperAdmin } = useRole();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: DRAWER_WIDTH, boxSizing: "border-box" },
      }}
    >
      <Toolbar />
      <List>
        {NAV_ITEMS.map((item) => (
          <ListItemButton key={item.to} component={NavLink} to={item.to} end={item.to === "/"}>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
      {isSuperAdmin && (
        <List subheader="Administration">
          {ADMIN_ITEMS.map((item) => (
            <ListItemButton key={item.to} component={NavLink} to={item.to}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      )}
    </Drawer>
  );
}
