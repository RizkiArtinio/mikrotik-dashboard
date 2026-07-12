import { Box, Toolbar } from "@mui/material";
import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <Box sx={{ display: "flex" }}>
      <Topbar />
      <Sidebar />
      <Box component="main" sx={{ flexGrow: 1, bgcolor: "background.default", minHeight: "100vh", p: 3 }}>
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}
