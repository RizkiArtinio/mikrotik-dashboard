import { Card, CardContent, LinearProgress, Stack, Typography } from "@mui/material";
import Grid from "@mui/material/Grid2";
import type { HealthSnapshot, ResourceSnapshot } from "@/types/dashboard";

function Gauge({ label, value, unit = "%" }: { label: string; value: number | null; unit?: string }) {
  const pct = value ?? 0;
  const color = pct > 90 ? "error" : pct > 75 ? "warning" : "primary";
  return (
    <Stack spacing={0.5}>
      <Stack direction="row" justifyContent="space-between">
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="body2" fontWeight={600}>
          {value === null ? "—" : `${value.toFixed(0)}${unit}`}
        </Typography>
      </Stack>
      <LinearProgress variant="determinate" value={Math.min(pct, 100)} color={color} />
    </Stack>
  );
}

export function ResourceGauges({
  resources,
  health,
}: {
  resources: ResourceSnapshot | null;
  health: HealthSnapshot | null;
}) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="subtitle1" fontWeight={700} gutterBottom>
          Router Resources
        </Typography>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Gauge label="CPU Usage" value={resources?.cpu_load ?? null} />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Gauge label="Memory Usage" value={resources?.memory_usage_percent ?? null} />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Gauge label="Disk Usage" value={resources?.disk_usage_percent ?? null} />
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Stack direction="row" spacing={3}>
              <Stack>
                <Typography variant="body2" color="text.secondary">
                  Voltage
                </Typography>
                <Typography variant="body1" fontWeight={600}>
                  {health?.voltage != null ? `${health.voltage.toFixed(1)} V` : "—"}
                </Typography>
              </Stack>
              <Stack>
                <Typography variant="body2" color="text.secondary">
                  Temperature
                </Typography>
                <Typography variant="body1" fontWeight={600}>
                  {health?.temperature != null ? `${health.temperature.toFixed(0)} °C` : "—"}
                </Typography>
              </Stack>
            </Stack>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
