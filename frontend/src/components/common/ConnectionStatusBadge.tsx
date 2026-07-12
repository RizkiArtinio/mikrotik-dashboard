import { Chip } from "@mui/material";

export function ConnectionStatusBadge({ connected }: { connected: boolean }) {
  return (
    <Chip
      size="small"
      label={connected ? "Live" : "Polling (fallback)"}
      color={connected ? "success" : "warning"}
      variant={connected ? "filled" : "outlined"}
    />
  );
}
