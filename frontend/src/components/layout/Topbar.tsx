import LogoutIcon from "@mui/icons-material/Logout";
import { AppBar, Box, IconButton, Toolbar, Typography } from "@mui/material";
import { useAuth } from "@/hooks/useAuth";
import { RouterSwitcher } from "./RouterSwitcher";

export function Topbar() {
  const { user, logout } = useAuth();

  return (
    <AppBar position="fixed" color="default" elevation={1} sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}>
      <Toolbar sx={{ gap: 2 }}>
        <Typography variant="h6" noWrap sx={{ flexGrow: 0, fontWeight: 700 }}>
          MikroTik Dashboard
        </Typography>
        <Box flexGrow={1} />
        <RouterSwitcher />
        <Typography variant="body2" color="text.secondary">
          {user?.email} · {user?.role}
        </Typography>
        <IconButton onClick={logout} title="Logout">
          <LogoutIcon />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}
