import { MenuItem, TextField } from "@mui/material";
import { useEffect } from "react";
import { useRouterSelection } from "@/hooks/useRouterSelection";
import { useRouters } from "@/hooks/useRouters";

export function RouterSwitcher() {
  const { data: routers } = useRouters();
  const { routerId, setRouterId } = useRouterSelection();

  useEffect(() => {
    if (routerId === null && routers && routers.length > 0) {
      setRouterId(routers[0].id);
    }
  }, [routerId, routers, setRouterId]);

  if (!routers || routers.length === 0) return null;

  return (
    <TextField
      select
      size="small"
      value={routerId ?? ""}
      onChange={(e) => setRouterId(Number(e.target.value))}
      sx={{ minWidth: 220, bgcolor: "background.paper", borderRadius: 1 }}
    >
      {routers.map((r) => (
        <MenuItem key={r.id} value={r.id}>
          {r.name} ({r.ip_address})
        </MenuItem>
      ))}
    </TextField>
  );
}
