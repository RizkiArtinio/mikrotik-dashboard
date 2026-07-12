import { Alert, Divider, Stack, Typography } from "@mui/material";
import Grid from "@mui/material/Grid2";
import { useState } from "react";
import { QrCodeDisplay } from "@/components/vpn/QrCodeDisplay";
import { VpnConfigDisplay } from "@/components/vpn/VpnConfigDisplay";
import { VpnGeneratorForm } from "@/components/vpn/VpnGeneratorForm";
import { useRouterSelection } from "@/hooks/useRouterSelection";
import type { WireguardPeerResult } from "@/types/vpn";

export default function VpnGeneratorPage() {
  const { routerId } = useRouterSelection();
  const [result, setResult] = useState<WireguardPeerResult | null>(null);

  if (routerId === null) return <Alert severity="info">Select a router first.</Alert>;

  return (
    <Stack spacing={3}>
      <Typography variant="h5" fontWeight={700}>
        Create WireGuard Peer
      </Typography>
      <Grid container spacing={4}>
        <Grid size={{ xs: 12, md: 5 }}>
          <VpnGeneratorForm routerId={routerId} onGenerated={setResult} />
        </Grid>
        <Grid size={{ xs: 12, md: 7 }}>
          {result ? (
            <Stack spacing={2}>
              <Typography variant="subtitle1" fontWeight={700}>
                {result.peer.peer_name} — Client Configuration
              </Typography>
              <Stack direction={{ xs: "column", sm: "row" }} spacing={3} alignItems="flex-start">
                <QrCodeDisplay base64Png={result.qr_code_base64} />
                <Divider orientation="vertical" flexItem sx={{ display: { xs: "none", sm: "block" } }} />
                <VpnConfigDisplay configText={result.config_text} peerName={result.peer.peer_name} />
              </Stack>
            </Stack>
          ) : (
            <Alert severity="info">Fill the form and click Generate to create a new peer.</Alert>
          )}
        </Grid>
      </Grid>
    </Stack>
  );
}
