import { Card, CardContent, Chip, Stack, Typography } from "@mui/material";
import Grid from "@mui/material/Grid2";
import type { IspPingResult } from "@/types/misc";

export function IspStatusPanel({ results }: { results: IspPingResult[] }) {
  return (
    <Grid container spacing={2}>
      {results.map((r) => (
        <Grid key={r.target} size={{ xs: 12, sm: 6, md: 4 }}>
          <Card variant="outlined">
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Typography variant="subtitle2">{r.label}</Typography>
                <Chip size="small" label={r.status} color={r.status === "up" ? "success" : "error"} />
              </Stack>
              <Typography variant="body2" color="text.secondary" mt={1}>
                {r.target}
              </Typography>
              <Stack direction="row" spacing={3} mt={1}>
                <Stack>
                  <Typography variant="caption" color="text.secondary">
                    Latency
                  </Typography>
                  <Typography variant="body1" fontWeight={600}>
                    {r.latency_ms != null ? `${r.latency_ms} ms` : "—"}
                  </Typography>
                </Stack>
                <Stack>
                  <Typography variant="caption" color="text.secondary">
                    Packet Loss
                  </Typography>
                  <Typography variant="body1" fontWeight={600}>
                    {r.packet_loss_percent != null ? `${r.packet_loss_percent}%` : "—"}
                  </Typography>
                </Stack>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
