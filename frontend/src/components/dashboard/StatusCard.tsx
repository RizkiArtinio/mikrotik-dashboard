import { Card, CardContent, Stack, Typography } from "@mui/material";
import type { ReactNode } from "react";

export function StatusCard({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value: ReactNode;
  icon?: ReactNode;
  color?: string;
}) {
  return (
    <Card variant="outlined" sx={{ height: "100%" }}>
      <CardContent>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          {icon && <Stack sx={{ color: color ?? "primary.main" }}>{icon}</Stack>}
          <Stack>
            <Typography variant="body2" color="text.secondary">
              {label}
            </Typography>
            <Typography variant="h5" fontWeight={700} sx={{ color }}>
              {value}
            </Typography>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
